## OverTheYears
**Status:** In progress!<br>
A deep dive into an artist's discography and the associated audio features for each song of each album.

## Motivation
An exercise in data visualization. Wanted practice using different programming languages (Javascript) and libraries (Pandas for Python) and to try my hand at implementing scrollytelling, an online visual storytelling experience, after seeing articles from [The Pudding](https://pudding.cool).

## Installation & Setup
### Get API Keys
1. [Spotify](https://developer.spotify.com/dashboard/login)
  - To get albums, tracks and audio features for an artist.
  - Store credentials as environment variables called `CLIENT_ID` and `CLIENT_SECRET`.
2. [MusixMatch](https://developer.musixmatch.com)
  - For getting the lyrics of each track.
  - Store api key as environment variable called `MUSIXMATCH_KEY`.
3. [Microsoft Azure](https://azure.microsoft.com/en-us/free/cognitive-services/)
  - For using their Text Analytics library, which supports multiple languages including English and Korean.
  - Store key and endpoint as `AZURE_KEY` and `AZURE_ENDPOINT` respectively.

### Run Program
1. First install pipenv if needed as shown [here](https://pypi.org/project/pipenv/).
1. Clone repository and navigate into it.
1. Install project dependancies:<br>
`pipenv install`
1. Activate project's virtual environment:<br>
`pipenv shell`
1. This particular project looks at BTS' discography; if you want to get another artist's discography, replace the `ARTIST_ID` variable's value with a different artist's ID.
  1. Get artist ID by opening Spotify > Going to the artist's page > Clicking the ellipsis button > Share > Copy Spotify URI
  1. Everything after "spotify:artist:" is the ID for that particular artist.
1. Run code:<br>
`python3 main.py` 