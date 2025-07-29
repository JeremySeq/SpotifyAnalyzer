import os
from collections import Counter
from datetime import datetime
from functools import lru_cache

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Put your Spotify developer credentials here:
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def fetch_playlist_info(playlist_id: str) -> dict:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = Spotify(auth_manager=auth_manager)

    playlist_meta = sp.playlist(playlist_id)
    playlist_name = playlist_meta.get("name", "Unknown Playlist")
    playlist_owner = playlist_meta.get("owner", {}).get("display_name", "Unknown Owner")

    tracks = []
    results = sp.playlist_items(playlist_id, limit=100)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    simplified_tracks = []
    for item in tracks:
        t = item.get("track")
        if not t:
            continue
        simplified_tracks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "duration_ms": t.get("duration_ms"),
            "preview_url": t.get("preview_url"),
            "explicit": t.get("explicit", False),

            "album": {
                "name":  t.get("album", {}).get("name"),
                "release_date": t.get("album", {}).get("release_date")
            },

            "artists": [
                {"id": a.get("id"), "name": a.get("name")}
                for a in t.get("artists", [])
            ],
        })

    @lru_cache(maxsize=4096)
    def get_artist_genres(artist_id):
        artist = sp.artist(artist_id)
        return artist.get("genres", [])

    def extract_year(release_date):
        if not release_date:
            return None
        try:
            return int(release_date[:4])
        except ValueError:
            return None

    artists_counter = Counter()
    years_counter = Counter()
    durations = []
    genres_counter = Counter()

    now_year = datetime.now().year
    throwback_count = 0
    freshness_count = 0
    explicit_count = 0
    total_artists = 0

    for track in simplified_tracks:
        artist_objs = track.get("artists", [])
        artist_names = [a["name"] for a in artist_objs]
        artists_counter.update(artist_names)

        total_artists += len(artist_objs)

        year = extract_year(track.get("album", {}).get("release_date"))
        if year:
            years_counter[year] += 1
            if now_year - year >= 10:
                throwback_count += 1
            if now_year - year <= 2:
                freshness_count += 1

        if duration := track.get("duration_ms"):
            durations.append(duration)

        if track.get("explicit"):
            explicit_count += 1

        for artist in artist_objs:
            genres_counter.update(get_artist_genres(artist["id"]))

    total_tracks = len(simplified_tracks)
    top_3_artists = [name for name, _ in artists_counter.most_common(3)]
    top_3_artist_track_count = sum(
        1 for track in simplified_tracks if any(a["name"] in top_3_artists for a in track.get("artists", []))
    )

    return {
        "playlist_name": playlist_name,
        "playlist_id": playlist_id,
        "playlist_owner": playlist_owner,
        "analyzed_at": datetime.now().isoformat(),
        "tracks": simplified_tracks,

        "total_tracks": total_tracks,
        "top_artists": artists_counter.most_common(10),
        "year_distribution": dict(sorted(years_counter.items())),
        "average_duration_ms": int(sum(durations) / len(durations)) if durations else 0,
        "top_genres": genres_counter.most_common(10),

        "throwback_index": round((throwback_count / total_tracks) * 100, 2) if total_tracks else 0,
        "explicit_energy": round((explicit_count / total_tracks) * 100, 2) if total_tracks else 0,
        "artist_concentration": round((top_3_artist_track_count / total_tracks) * 100, 2) if total_tracks else 0,
        "freshness_score": round((freshness_count / total_tracks) * 100, 2) if total_tracks else 0,
        "collab_score": round(total_artists / total_tracks, 2) if total_tracks else 0,
    }
