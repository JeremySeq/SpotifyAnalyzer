import { useState, useEffect } from "react";
import "./App.css";
import API_SERVER from "./Constants.jsx";
import Analysis from "./Analysis.jsx";

export default function App() {
    const [input,   setInput]   = useState("");
    const [stats,   setStats]   = useState(null);
    const [loading, setLoading] = useState(false);
    const [error,   setError]   = useState("");

    // fetch by analysis ID from URL
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
            const res = await fetch(`${API_SERVER}/api/playlist/${playlistId}`);
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || "Failed to fetch playlist analysis");
            }

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
        if (!playlistId) return setError("Enter a playlist URL.");
        fetchPlaylistAnalysis(playlistId);
    };

    return (
        <div className="container">
            <h1>Spotify Playlist Analyzer</h1>

            <form onSubmit={onSubmit} className="form">
                <input
                    className="input"
                    placeholder="Paste Spotify playlist URL"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button className="submit" type="submit">Analyze</button>
            </form>

            <p className="hint">Must be a public playlist.</p>

            {loading && <p className="info">Fetching analysis…</p>}
            {error && <p className="info error">{error}</p>}
            {stats && <Analysis stats={stats} />}
        </div>
    );
}
