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
    # (1) Get access token
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
        # Whoops it wasn't a 200
        print("Error when trying to get access token")
        raise
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']

    # (2) MAKE API CALLS FOR DATA - BTS
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    BASE_URL = 'https://api.spotify.com/v1/'
    ARTIST_ID = '3Nrfpe0tUJi4K4DXYWgMUX'

    # Get all albums
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
        tracks = requests.get(BASE_URL + 'albums/{id}/tracks'.format(id=album['id']), headers=headers)
        try:
            tracks.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Error when trying to retrieve tracks for the album: {album}".format(album=album['name']))
            raise

        for track in tracks.json()['items']:
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
                'album_name': album['name'],
                'release_date': album['release_date'],
                'album_id': album['id'],
                'popularity': track_info['popularity']
            })
            data.append(all_details_for_track)

    # Save data
    with open(DISCOGRAPHY_FILE_NAME, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    # Uncomment if you need to get discography data first
    # get_data()

    # Convert to list of dicts to DataFrame (2D table with labeled axes) 
    df = pd.read_json(DISCOGRAPHY_FILE_NAME)
    print(df.head())
    print(df.columns)
