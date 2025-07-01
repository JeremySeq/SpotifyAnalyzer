const CLIENT_ID     = "499bae4810ff41db826832dc66b2148e";
const REDIRECT_URI  = "http://192.168.1.23:5173";
const AUTH_ENDPOINT = "https://accounts.spotify.com/authorize";
const RESPONSE_TYPE = "token";
const SCOPES        = ["playlist-read-private"].join(" ");

export default function SpotifyLogin() {
    const loginUrl =
        `${AUTH_ENDPOINT}?client_id=${CLIENT_ID}` +
        `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
        `&scope=${encodeURIComponent(SCOPES)}` +
        `&response_type=${RESPONSE_TYPE}`;

    return (
        <a className="login-button" href={loginUrl}>
            Log in with Spotify
        </a>
    );
}
