## OverTheYears
_**Still in progress!**_<br>
A deep dive into an artist's discography and the associated audio features for each song of each album.

## Motivation
An exercise in data visualization. Wanted practice using different programming languages (Javascript) and libraries (Pandas for Python) and to try my hand at implementing scrollytelling, an online visual storytelling experience, after seeing articles from [The Pudding](https://pudding.cool).

## Installation & Setup
1. First install pipenv if needed as shown [here](https://pypi.org/project/pipenv/).
1. Clone repository and navigate into it.
1. Install project dependancies:<br>
`pipenv install`
1. Activate project's virtual environment:<br>
`pipenv shell`
1. Go through Spotify For Developers to get client credentials and store it as environmental variables `CLIENT_ID` and `CLIENT_SECRET`.
1. This particular project looks at BTS' discography; if you want to get another artist's discography, replace the `ARTIST_ID` variable's value with a different artist's ID.
  1. Get artist ID by opening Spotify > Going to the artist's page > Clicking the ellipsis button > Share > Copy Spotify URI
  1. Everything after "spotify:artist:" is the ID for that particular artist.
1. Run code:<br>
`python3 main.py` 