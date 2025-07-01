import requests
import json
import re
import logging

MOODS = [
    "Joyful", "Happy", "Uplifting", "Sad", "Melancholic", "Somber",
    "Angry", "Frustrated", "Aggressive", "Romantic", "Loving", "Passionate",
    "Reflective", "Thoughtful", "Introspective", "Energetic", "Excited", "Pumped",
    "Calm", "Relaxed", "Chill", "Dark", "Moody", "Brooding"
]
API_URL = "https://ai.hackclub.com/chat/completions"

def sanitize(text: str) -> str:
    """Clean up text for URL and processing."""
    return re.sub(r"[\"']", "", text).strip().lower()

def get_lyrics(song: str, artist: str, timeout=5) -> str | None:
    """Fetch lyrics from lyrics.ovh API."""
    url = f"https://api.lyrics.ovh/v1/{sanitize(artist)}/{sanitize(song)}"
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code != 200:
            return None
        return r.json().get("lyrics")
    except requests.RequestException:
        return None

def analyze_lyrics_mood(lyrics: str) -> dict:
    """
    Sends the given lyrics to ai.hackclub.com API for sentiment analysis.
    Returns a dict with a single key "mood" whose value is one mood word from the list.
    """

    if lyrics is None:
        return {"mood": "No lyrics"}

    headers = {"Content-Type": "application/json"}

    prompt = (
        "Analyze the sentiment of the following song lyrics. "
        "From this list of moods, choose exactly one mood that best describes the overall mood of the lyrics:\n"
        f"{', '.join(MOODS)}.\n"
        "Respond ONLY with a valid JSON object with a single key \"mood\" and the mood word as the value. "
        "Do NOT include any explanation or extra text.\n\n"
        f"Lyrics:\n{lyrics}\n\n"
        "JSON response:"
    )

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that analyzes song lyrics sentiment."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50,
        "temperature": 0
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()

    raw_response = result["choices"][0]["message"]["content"].strip()

    # Parse JSON safely
    try:
        sentiment_json = json.loads(raw_response)
    except json.JSONDecodeError:
        # fallback: return empty mood or raw text
        sentiment_json = {"mood": "Unknown"}

    return sentiment_json

def build_batch_prompt(items):
    """
    Create the GPT prompt for batch mood classification.
    items: list of (track_id, lyrics)
    """
    parts = [
        "Analyze each set of lyrics below and reply ONLY with a JSON object "
        "mapping track_id to one mood word from this list:\n"
        + ", ".join(MOODS) + ".\n"
    ]
    for tid, lyr in items:
        lyr = lyr or "No lyrics available."
        parts.append(f"Track ID: {tid}\nLyrics:\n{lyr}\n")
    parts.append("JSON response:")
    return "\n".join(parts)

def analyze_lyrics_moods_batch(items):
    """
    items: list of (track_id, lyrics)
    Returns: dict mapping track_id to mood string
    """
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You label song lyrics with exactly one mood from the provided list."},
            {"role": "user", "content": build_batch_prompt(items)}
        ],
        "max_tokens": 1000,
        "temperature": 0,
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return json.loads(text)
    except Exception as e:
        logging.warning(f"GPT batch request failed: {e}")
        # Return fallback: unknown moods for all tracks
        return {tid: "Unknown" for tid, _ in items}

def chunked(iterable, size):
    """Yield successive chunks of size `size` from iterable."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]

def analyze_all_tracks_in_batches(tracks, batch_size=6):
    """
    tracks: list of dicts with 'id', 'name', 'artist'
    batch_size: how many tracks to send per GPT request
    """
    all_results = {}

    for chunk in chunked(tracks, batch_size):
        lyrics_batch = [
            (t["id"], get_lyrics(t["name"], t["artist"]))
            for t in chunk
        ]
        batch_result = analyze_lyrics_moods_batch(lyrics_batch)
        all_results.update(batch_result)

    return all_results
