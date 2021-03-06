from numpy.lib.shape_base import split
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from flask import Flask, jsonify, request, render_template
import pandas as pd
import requests
import uuid
import json
import os

app = Flask(__name__)
DISCOGRAPHY_FILE_NAME = 'bts_songs.json'
ALBUMS_TO_EXCLUDE = ['Skool Luv Affair (Special Edition)', 'Wake Up (Standard Edition)', 'Youth', 'FACE YOURSELF', 'MAP OF THE SOUL : 7 ~ THE JOURNEY ~']
PITCH_CLASSES = {
  0: "C",
  1: "C#",
  2: "D",
  3: "D#",
  4: "E",
  5: "F",
  6: "F#",
  7: "G",
  8: "G#",
  9: "A",
  10: "A#",
  11: "B"
}

"""
Gets all of an artists' songs and other data (audio features, associated album info) using Spotify's API and stores JSON result
in a file. Must register at Spotify for Developers, Microsoft Azure and MusixMatch first for it to work properly as stated in the README.
Used following article as a starting point for getting data into dataframe: https://stmorse.github.io/journal/spotify-api.html
"""
def get_data():
    # (1) SET UP CLIENT & GET ACCESS TOKEN
    AUTH_URL = 'https://accounts.spotify.com/api/token'
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    try:
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error when trying to get access token")
        raise
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']

    # Setup client for Microsoft Azure's Text Analytics library
    text_analytics_client = authenticate_client()

    # (2) MAKE API CALLS FOR DATA 
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    BASE_URL = 'https://api.spotify.com/v1/'
    ARTIST_ID = '3Nrfpe0tUJi4K4DXYWgMUX' # BTS' SPOTIFY ARTIST ID

    # Get all albums for artist
    res = requests.get(BASE_URL + 'artists/{id}/albums'.format(id=ARTIST_ID), 
                        headers=headers,
                        params={'include_groups': 'album', 'limit': 50, 'country': 'SK'})
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error when trying to retrieve albums")
        raise

    data = []
    # Get tracks in each album
    for album in res.json()['items']:
        if album['name'] in ALBUMS_TO_EXCLUDE:
            # Only want Korean albums - not Japanese or special editions
            continue

        album_info = requests.get(BASE_URL + 'albums/{id}'.format(id=album['id']), headers=headers)
        try:
            album_info.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Error when trying to retrieve further album details for the album: {album}".format(album=album['name']))
            raise        
        album_info = album_info.json()

        for track in album_info['tracks']['items']:
            # Skip over skits
            if track['name'].lower().find('skit') != -1:
                continue
            
            # Get popularity
            track_info = requests.get(BASE_URL + 'tracks/{id}'.format(id=track['id']), headers=headers) 
            try:
                track_info.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Error when trying to retrieve further track details for the track: {track}".format(track=track['name']))
                raise   
            track_info = track_info.json()

            # Get audio features for each track
            audio_features = requests.get(BASE_URL + 'audio-features/{id}'.format(id=track['id']), headers=headers)
            try:
                audio_features.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Error when trying to retrieve audio features for the track: {track}".format(track=track['name']))
                raise        
            all_details_for_track = audio_features.json()

            # Get lyrics and sentiment analysis scores
            lyric_analysis = get_and_analyze_lyrics(text_analytics_client, track['name'], 'bts')

            # Add extra details to access later
            all_details_for_track.update({
                'track_name': track['name'],
                'track_popularity': track_info['popularity'],
                'album_name': album['name'],
                'album_release_date': album['release_date'],
                'album_id': album['id'],
                'album_popularity': album_info['popularity'],
                'lyrics': lyric_analysis['lyrics'],
                'document_sentiment': lyric_analysis['document_sentiment'],
                'pos_score': lyric_analysis['pos_score'],
                'neg_score': lyric_analysis['neg_score'],
                'neutral_score': lyric_analysis['neutral_score']
            })
            print("FINISHED ANALYSING " + track['name'])
            data.append(all_details_for_track)

    # (3) SAVE DATA AS JSON FILE
    with open(DISCOGRAPHY_FILE_NAME, 'w') as f:
        json.dump(data, f)

"""
Create and authenticate TextAnalyticsClient as per the following how to: 
https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/quickstarts/text-analytics-sdk?tabs=version-3-1&pivots=programming-language-python
This will allow us to perform sentiment analysis on Korean text--needed because BTS is a Korean group. 
"""
def authenticate_client():
    ta_credential = AzureKeyCredential(os.environ.get('AZURE_KEY'))
    text_analytics_client = TextAnalyticsClient(
            endpoint=os.environ.get('AZURE_ENDPOINT'), 
            credential=ta_credential)
    return text_analytics_client

"""
Get lyrics from MusixMatch API and perform sentiment analysis on it with Microsoft's Text Analytics API. 
Returns lyrics, overall document (lyric) sentiment, and confidence scores.
"""
def get_and_analyze_lyrics(client, song_title, singer):
    BASE_URL = 'https://api.musixmatch.com/ws/1.1/'
    API_KEY = os.environ.get('MUSIXMATCH_KEY')

    # Must take into account that BTS' 2nd Grade is stored in MusixMatch as 'Second Grade'
    song_title = 'Second Grade' if (song_title == '2nd Grade') else song_title
    GET_LYRICS_URL = 'matcher.lyrics.get?format=json&callback=callback&q_artist={artist}&q_track={song}&apikey={api_key}'.format(
        artist=singer, 
        song=song_title, 
        api_key=API_KEY
    )
    res = requests.get(BASE_URL + GET_LYRICS_URL)
    invalid_ret = {
        'lyrics': '',
        'document_sentiment': '',
        'pos_score': -1.0,
        'neg_score': -1.0,
        'neutral_score': -1.0
    }

    if len(res.json()['message']['body']) == 0 or res.json()['message']['body']['lyrics']['lyrics_body'] == '':
        # MusixMatch did not find lyrics - either because it could not find song or the song had no lyrics (instrumental only) 
        return invalid_ret
    
    # Found valid lyrics - format it by removing unnecessary breaks + warning at end
    lyrics = res.json()['message']['body']['lyrics']['lyrics_body']
    lyrics = lyrics.replace('\n\n', ' ').replace('\n', ' ')
    lyrics = lyrics[:lyrics.find(' ...')]

    # Use Microsoft's Text Analytics API to get sentiment analysis of (Korean!) text
    response = client.analyze_sentiment(documents=[lyrics])[0]

    if (response is None) or (not bool(response)):
        # Was not able to perform sentiment analysis successfully - should technically never be reached as long as lyrics isn't empty
        invalid_ret['lyrics'] = lyrics
        return invalid_ret
    else:
        ret = {
            'lyrics': lyrics,
            'document_sentiment': response.sentiment,
            'pos_score': response.confidence_scores.positive,
            'neg_score': response.confidence_scores.negative,
            'neutral_score': response.confidence_scores.neutral
        }
        return ret

@app.route('/')
def index():
    hello = "hello world"
    return render_template('index.html', end="this is the end!")

@app.route('/albm_avg_data', methods=['GET'])
def get_album_aft_averages():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    # to_json() renders a json string so you need to wrap it in json.loads() to get the actual json object
    return json.loads(df.to_json())

@app.route('/basic_info', methods=['GET'])
def get_basic_info():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique()
    # to_json() renders a json string so you need to wrap it in json.loads() to get the actual json object
    return json.loads(albums)

@app.route('/popularity', methods=['GET'])
def get_popularity():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique()
    # to_json() renders a json string so you need to wrap it in json.loads() to get the actual json object
    print(df[['track_name', 'album_name', 'track_popularity']])
    return json.loads(albums)    

@app.route('/key_changes', methods=['GET'])
def get_key_changes():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique().tolist()
    ret = {}
    ret['album_name'] = albums

    df = df[['track_name', 'album_name', 'album_release_date', 'key', 'mode']]
    temp = df.loc[df['album_name'] == 'MAP OF THE SOUL : 7']
    #print(temp)
    for album in albums:
        # get all rows of songs that belong to one album
        curr = df.loc[df['album_name'] == album]
        for pitch in PITCH_CLASSES:
            num_songs_with_pitch = int(curr[curr['key'] == pitch].count()['key'])
            if pitch not in ret:
                ret[pitch] = [num_songs_with_pitch]
            else:
                ret[pitch].append(num_songs_with_pitch)
    #print(ret)
    return json.dumps(ret)

@app.route('/mode_changes', methods=['GET'])
def get_mode_changes():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique().tolist()
    #print(albums.tolist())
    #print(list(df.columns))
    ret = {}
    ret['album_name'] = albums

    df = df[['track_name', 'album_name', 'album_release_date', 'key', 'mode']]
    temp = df.loc[df['album_name'] == 'MAP OF THE SOUL : 7']
    #print(temp[['track_name', 'mode']])
    for album in albums:
        # get all rows of songs that belong to one album
        curr = df.loc[df['album_name'] == album]
        total_num_songs = len(curr.index)
        num_songs_in_major = curr[curr['mode'] == 1].count()['mode']
        #print("{} songs in major key, {} songs in minor key".format(num_songs_in_major, (total_num_songs - num_songs_in_major)))

        # add up number of songs with each pitch for each album
        for pitch in PITCH_CLASSES:
            songs_in_major_key = int(curr[(curr['key'] == pitch) & (curr['mode'] == 1)].count()['key'])
            songs_in_minor_key = int(curr[(curr['key'] == pitch) & (curr['mode'] == 0)].count()['key'])
            if pitch not in ret:
                ret[pitch] = {
                    'major': [songs_in_major_key],
                    'minor': [songs_in_minor_key]
                }
            else:
                ret[pitch]['major'].append(songs_in_major_key)
                ret[pitch]['minor'].append(songs_in_minor_key)
    #print(ret)
    return json.dumps(ret)    

@app.route('/speechiness', methods=['GET'])
def get_speechiness():
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique().tolist()
    #print(albums.tolist())
    print(list(df.columns))
    speechiness_df = df[['track_name', 'album_name', 'album_release_date', 'speechiness']]
    speechiness_df = speechiness_df.groupby(['album_name', 'album_release_date'], as_index=False)
    speechiness_df = speechiness_df['speechiness'].mean().round(3).sort_values('album_release_date')
    print(speechiness_df)
    ret = {}
    for album, speechiness in zip(speechiness_df['album_name'], speechiness_df['speechiness']):
        ret[album] = speechiness
    print(ret)
    return json.dumps(ret)

if __name__ == "__main__":
    # Uncomment if you need to get discography data first
    # NOTE: The only song that does not have associated sentiment analysis (as of 10/2020) is 'Interlude', because it doesn't have any lyrics
    # get_data()
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    # Convert to list of dicts to DataFrame (2D table with labeled axes) 
    print(list(df.columns))
    #get_popularity()
    #print(df.head()[['track_name', 'lyrics']])
    print(df[df['track_name'] == 'Jamais Vu']['lyrics'][3])
    #get_mode_changes()
    
    #print(df.loc[df['album_name'] == 'MAP OF THE SOUL : 7'])
    # translator? https://docs.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator?tabs=python#transliterate-text


    """
    audio_feature_titles = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
    total_songs = 0
    total_albums = 0    

    # calculate average of audio features for each group of rows (aka each album) - as_index=False gives df instead of series
    temp = df.groupby(['album_name', 'album_release_date'], as_index=False)[audio_feature_titles].mean()
    temp = temp.sort_values(by='speechiness')
    print(temp)"""

    #    app.run("0.0.0.0", "5010")


