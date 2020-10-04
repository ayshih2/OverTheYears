from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd
import requests
import json
import os

DISCOGRAPHY_FILE_NAME = 'bts_songs.json'

"""
Gets all of an artists' songs and other data (audio features, associated album info) using Spotify's API and stores JSON result
in a file. Must register at Spotify for Developers first for it to work properly because you all API calls need a valid client id and client secret.
Used following article as a starting point: https://stmorse.github.io/journal/spotify-api.html
"""
def get_data():
    # (1) GET ACCESS TOKEN
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

    # (2) MAKE API CALLS FOR DATA 
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    BASE_URL = 'https://api.spotify.com/v1/'
    ARTIST_ID = '3Nrfpe0tUJi4K4DXYWgMUX' # BTS' ID

    # Get all albums for artist
    res = requests.get(BASE_URL + 'artists/{id}/albums'.format(id=ARTIST_ID), 
                        headers=headers,
                        params={'include_groups': 'album', 'limit': 50, 'country': 'SK'})
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error when trying to retrieve albums")
        raise

    albums_to_exclude = ['Skool Luv Affair (Special Edition)', 'Wake Up (Standard Edition)', 'Youth', 'FACE YOURSELF', 'MAP OF THE SOUL : 7 ~ THE JOURNEY ~']
    data = []
    # Get tracks in each album
    for album in res.json()['items']:
        if album['name'] in albums_to_exclude:
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
            if track['name'].lower().find('skit') != -1:
                # skip over skits, get only music
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

            # Add extra details for future reference
            all_details_for_track.update({
                'track_name': track['name'],
                'track_popularity': track_info['popularity'],
                'album_name': album['name'],
                'album_release_date': album['release_date'],
                'album_id': album['id'],
                'album_popularity': album_info['popularity']
            })
            data.append(all_details_for_track)

    # Save data
    with open(DISCOGRAPHY_FILE_NAME, 'w') as f:
        json.dump(data, f)

def authenticate_client():
    ta_credential = AzureKeyCredential(os.environ.get('AZURE_KEY'))
    text_analytics_client = TextAnalyticsClient(
            endpoint=os.environ.get('AZURE_ENDPOINT'), 
            credential=ta_credential)
    return text_analytics_client

def get_lyrics(client):
    BASE_URL = 'https://api.musixmatch.com/ws/1.1/'
    API_KEY = os.environ.get('MUSIXMATCH_KEY')
    GET_TRACK_BASE_URL = 'matcher.track.get?format=json&callback=callback&q_artist=bts&q_track={song}&apikey={api_key}'.format(song='springday', api_key=API_KEY)

    q_track = 'q_track=dynamite'
    res = requests.get(BASE_URL + GET_TRACK_BASE_URL)
    data = res.json()
    id = data['message']['body']['track']['commontrack_id']
    #print(data['message']['body']['track']['commontrack_id'])

    GET_LYRICS_URL = 'matcher.lyrics.get?format=json&callback=callback&q_artist=bts&q_track={song}&apikey={api_key}'.format(song='truth untold', api_key=API_KEY)

    res = requests.get(BASE_URL + GET_LYRICS_URL)
    lyrics = res.json()['message']['body']['lyrics']['lyrics_body']
    lyrics = lyrics.replace('\n\n', ' ').replace('\n', ' ')
    lyrics = lyrics[:lyrics.find(' ...')]
    print(lyrics)

    # https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/quickstarts/text-analytics-sdk?tabs=version-3-1&pivots=programming-language-python
    response = client.analyze_sentiment(documents=[lyrics])[0]
    print("Document Sentiment: {}".format(response.sentiment))
    print("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        response.confidence_scores.positive,
        response.confidence_scores.neutral,
        response.confidence_scores.negative,
    ))
    for idx, sentence in enumerate(response.sentences):
        print("Sentence: {}".format(sentence.text))
        print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
        print("Sentence score:\nPositive={0:.2f}\nNeutral={1:.2f}\nNegative={2:.2f}\n".format(
            sentence.confidence_scores.positive,
            sentence.confidence_scores.neutral,
            sentence.confidence_scores.negative,
        ))
        print(idx)

if __name__ == "__main__":
    # Uncomment if you need to get discography data first
    #get_data()

    # Convert to list of dicts to DataFrame (2D table with labeled axes) 
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    albums = df.album_name.unique()

    audio_feature_titles = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
    total_songs = 0
    total_albums = 0
    for album in albums:
        print(album)
        total_albums += 1
        tracks = df.loc[df['album_name'] == album]
        total_songs += len(tracks.index)
        #print(tracks)

    print("There are {} songs".format(total_songs))

    # Use Microsoft Azure's Text Analytics library
    #client = authenticate_client()
    #get_lyrics(client)
    
    #print(tracks[['track_name', 'danceability', 'valence', 'energy']])
    #audio_features_df = (df.ix['MAP OF THE SOUL : 7 ~ THE JOURNEY ~'])[['danceability', 'energy', 'track_name']]
    #audio_features_df = df.loc[[df['album_name'] == 'MAP OF THE SOUL : 7 ~ THE JOURNEY ~'], ['danceability', 'energy', 'track_name']]
    #print(audio_features_df)

