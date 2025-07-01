from flask import Blueprint, request, jsonify

import playlist_analysis as pa
from analysis_store import save_analysis_result, load_analysis_result

api = Blueprint('api', __name__)

SPOTIFY_API_BASE = "https://api.spotify.com/v1"

@api.route("/playlist/<playlist_id>")
def playlist_analysis_route(playlist_id: str):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ", 1)[1]

    try:
        stats = pa.analyze_playlist(playlist_id, token)
        if not stats:
            return jsonify({"error": "Playlist not found or empty"}), 404
        analysis_id = save_analysis_result(stats)
        stats["analysis_id"] = analysis_id
        return stats
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@api.route("/analysis/<analysis_id>")
def get_analysis_by_id(analysis_id: str):
    try:
        result = load_analysis_result(analysis_id)
        if result is None:
            return jsonify({"error": "Analysis not found"}), 404
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
