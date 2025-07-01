import { useState, useEffect } from "react";
import "./App.css";
import API_SERVER from "./Constants.jsx";
import SpotifyLogin from "./SpotifyLogin.jsx";
import Analysis from "./Analysis.jsx";

export default function App() {
    const [token,   setToken]   = useState(null);
    const [input,   setInput]   = useState("");
    const [stats,   setStats]   = useState(null);
    const [loading, setLoading] = useState(false);
    const [error,   setError]   = useState("");

    useEffect(() => {
        const hash = window.location.hash;
        if (hash) {
            const params = new URLSearchParams(hash.slice(1));
            const accessToken = params.get("access_token");
            if (accessToken) {
                setToken(accessToken);
                window.history.replaceState(null, null, " ");
            }
        }
    }, []);

    useEffect(() => {
        const search = new URLSearchParams(window.location.search);
        const analysisId = search.get("analysis");
        if (analysisId) fetchAnalysisById(analysisId);
    }, []);

    const parsePlaylistId = (raw) => {
        try {
            const url = new URL(raw);
            return url.pathname.startsWith("/playlist/")
                ? url.pathname.split("/playlist/")[1].split("?")[0]
                : raw;
        } catch {
            return raw;
        }
    };

    async function fetchAnalysisById(id) {
        setLoading(true); setError(""); setStats(null);
        try {
            const res = await fetch(`${API_SERVER}/api/analysis/${id}`);
            if (!res.ok) throw new Error("Analysis not found");
            const data = await res.json();
            setStats(data);
        } catch (e) {
            setError(e.message || "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    async function fetchPlaylistAnalysis(playlistId) {
        setLoading(true);
        setError("");
        setStats(null);
        try {
            // analysis
            const res = await fetch(
                `${API_SERVER}/api/playlist/${playlistId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (!res.ok) throw new Error("Failed to fetch playlist analysis");
            const data = await res.json();
            setStats(data);
            // set analysis id in url
            if (data.analysis_id) {
                const newUrl = `${window.location.pathname}?analysis=${data.analysis_id}`;
                window.history.pushState({}, "", newUrl);
            }
        } catch (e) {
            setError(e.message || "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    const onSubmit = (e) => {
        e.preventDefault();
        const playlistId = parsePlaylistId(input.trim());
        if (!playlistId) return setError("Enter a playlist URL or ID");
        if (!token)      return setError("You must log in with Spotify first");
        fetchPlaylistAnalysis(playlistId);
    };

    return (
        <div className="container">
            <h1>Spotify Playlist Analyzer</h1>

            {token ?
            <form onSubmit={onSubmit} className="form">
                <input
                    className="input"
                    placeholder="Paste Spotify playlist URL or ID"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button className="submit" type="submit">
                    Analyze
                </button>
            </form> : <SpotifyLogin />}

            {loading && <p className="info">Fetching analysis…</p>}
            {error && <p className="info error">{error}</p>}

            {stats && <Analysis stats={stats}/>}
        </div>
    );
}
