import os
from flask import Blueprint, send_from_directory, request, redirect


frontend = Blueprint('frontend', __name__)

frontend_dist_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')

# Serve static files
@frontend.route('/assets/<path:path>')
def serve_assets(path):
    """Serves static assets from /frontend/dist/assets"""
    return send_from_directory(os.path.join(frontend_dist_dir, 'assets'), path)

@frontend.route('/favicon.ico')
def favicon():
    # return "", 404
    return send_from_directory(
        os.path.join(frontend_dist_dir, 'assets'), 'favicon.ico')


@frontend.route('/', defaults={'path': ''})
@frontend.route('/<path:path>')
def serve(path):
    """Serves index.html main application file"""
    return send_from_directory(frontend_dist_dir, 'index.html')
