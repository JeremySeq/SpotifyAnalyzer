from datetime import datetime
import requests
from collections import Counter
from functools import lru_cache
from typing import List, Dict

SPOTIFY_API_BASE = "https://api.spotify.com/v1"

def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

def _spotify_get(url: str, token: str) -> dict:
    resp = requests.get(url, headers=_auth_headers(token), timeout=10)
    resp.raise_for_status()
    return resp.json()

def _get_playlist_tracks(playlist_id: str, token: str) -> List[dict]:
    url = f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks?limit=100"
    tracks = []
    while url:
        data = _spotify_get(url, token)
        tracks.extend(item["track"] for item in data["items"] if item.get("track"))
        url = data.get("next")
    return tracks

@lru_cache(maxsize=4_096)
def _get_artist_genres(artist_id: str, token: str) -> List[str]:
    url = f"{SPOTIFY_API_BASE}/artists/{artist_id}"
    return _spotify_get(url, token).get("genres", [])

def _extract_year(release_date: str | None) -> int | None:
    if not release_date:
        return None
    try:
        return int(release_date[:4])
    except ValueError:
        return None

def _get_playlist_metadata(playlist_id: str, token: str) -> dict:
    url = f"{SPOTIFY_API_BASE}/playlists/{playlist_id}"
    return _spotify_get(url, token)

def get_playlist_tracks(playlist_id: str, access_token: str) -> List[dict]:
    """
    Public helper – returns a **simplified but complete** list of track dicts.
    Each dict contains the fields required by `analyze_playlist`.
    """
    raw_tracks = _get_playlist_tracks(playlist_id, access_token)

    tracks: List[dict] = []
    for t in raw_tracks:
        tracks.append({
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
    return tracks


def analyze_playlist(playlist_id: str, access_token: str) -> dict:
    # Get playlist metadata
    playlist_meta = _get_playlist_metadata(playlist_id, access_token)
    playlist_name = playlist_meta.get("name", "Unknown Playlist")
    playlist_owner = playlist_meta.get("owner", {}).get("display_name", "Unknown Owner")

    tracks = get_playlist_tracks(playlist_id, access_token)
    if not tracks:
        return {}

    artists_counter = Counter()
    years_counter = Counter()
    durations = []
    genres_counter = Counter()

    now = datetime.now()
    now_year = now.year
    throwback_count = 0
    freshness_count = 0
    explicit_count = 0
    total_artists = 0

    for track in tracks:
        artist_objs = track.get("artists", [])
        artist_names = [a["name"] for a in artist_objs]
        artists_counter.update(artist_names)

        total_artists += len(artist_objs)

        year = _extract_year(track.get("album", {}).get("release_date"))
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
            genres_counter.update(_get_artist_genres(artist["id"], access_token))

    total_tracks = len(tracks)
    top_3_artists = [name for name, _ in artists_counter.most_common(3)]
    top_3_artist_track_count = sum(
        1 for track in tracks if any(a["name"] in top_3_artists for a in track.get("artists", []))
    )

    return {
        "playlist_name": playlist_name,
        "playlist_owner": playlist_owner,
        "analyzed_at": now.isoformat(),  # ISO 8601 timestamp of analysis time
        "tracks": tracks,

        "total_tracks": total_tracks,
        "top_artists": artists_counter.most_common(10),
        "year_distribution": dict(sorted(years_counter.items())),
        "average_duration_ms": int(sum(durations) / len(durations)) if durations else 0,
        "top_genres": genres_counter.most_common(10),

        "throwback_index": round((throwback_count / total_tracks) * 100, 2),
        "explicit_energy": round((explicit_count / total_tracks) * 100, 2),
        "artist_concentration": round((top_3_artist_track_count / total_tracks) * 100, 2),
        "freshness_score": round((freshness_count / total_tracks) * 100, 2),
        "collab_score": round(total_artists / total_tracks, 2),
    }
