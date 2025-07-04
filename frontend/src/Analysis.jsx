import React from "react";
import styles from "./Analysis.module.css";

import { BarChart } from "@mui/x-charts/BarChart";
import { PieChart } from "@mui/x-charts/PieChart";

const COLORS = ["#48b0ff", "#f8c550", "#ff7070", "#8b88ff", "#34d399"];

const msToMinSec = (ms) => {
    const min = Math.floor(ms / 60000);
    const sec = Math.floor((ms % 60000) / 1000).toString().padStart(2, "0");
    return `${min}:${sec}`;
};

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
    });
}

export default function Analysis({ stats }) {
    if (!stats) return null;

    const yearData = Object.entries(stats.year_distribution).map(([y, c]) => ({
        year: y,
        count: c,
    }));

    const genreData = stats.top_genres.map(([name, value], idx) => ({
        id: idx,
        value,
        label: name,
        color: COLORS[idx % COLORS.length],
    }));

    const artistData = stats.top_artists.map(([name, value], idx) => ({
        id: idx,
        value,
        label: name,
        color: COLORS[idx % COLORS.length],
    }));

    return (
        <>
            <header className={styles.playlistHeader}>
                <h2 className={styles.playlistName}>{stats.playlist_name}</h2>
                <p className={styles.playlistAuthor}>by {stats.playlist_owner}</p>
                <p>analyzed on {formatDate(stats.analyzed_at)}</p>
            </header>

            <div className={styles.analysisWrapper}>
                <section className={styles.statBlock}>
                    <h3>Overall</h3>
                    <p>
                        <strong>Total tracks:</strong> {stats.total_tracks}
                    </p>
                    <p>
                        <strong>Average duration:</strong>{" "}
                        {msToMinSec(stats.average_duration_ms)}
                    </p>
                </section>

                <section className={styles.statBlock}>
                    <h3>Year Distribution</h3>
                    <BarChart
                        height={310}
                        series={[
                            {
                                data: yearData.map((d) => d.count),
                                color: "var(--primary)", // bars color
                            },
                        ]}
                        xAxis={[
                            {
                                scaleType: "band",
                                data: yearData.map((d) => d.year),
                                tickLabelStyle: { fill: "var(--light-gray)" }, // x-axis labels
                                lineStyle: { stroke: "var(--light-gray)" },    // x-axis line
                            },
                        ]}
                        yAxis={[
                            {
                                tickLabelStyle: { fill: "var(--light-gray)" }, // y-axis labels
                                lineStyle: { stroke: "var(--light-gray)" },    // y-axis line
                            },
                        ]}
                        slotProps={{ legend: { hidden: true } }}
                        sx={{
                            ".MuiChartsAxis-tickLabel": { fontSize: 11, fill: "var(--light-gray)" },
                            ".MuiChartsAxis-line":      { stroke: "var(--light-gray)" },
                            ".MuiChartsGrid-line":      { stroke: "var(--light-gray)", opacity: 0.1 },
                        }}
                    />


                </section>

                <section className={styles.statBlock}>
                    <h3>Top Genres</h3>
                    <PieChart
                        height={310}
                        series={[
                            {
                                data: genreData,
                                innerRadius: 20,
                                outerRadius: 100,
                                paddingAngle: 2,
                            },
                        ]}
                        colors={COLORS}
                        legend={{ position: "bottom" }}
                        sx={{
                            '& .MuiChartsLegend-root, & .MuiChartsTooltip-root': {
                                color: 'var(--light-gray)', // legend and tooltip text
                            },
                        }}
                    />
                </section>

                <section className={styles.statBlock}>
                    <h3>Top Artists</h3>
                    <PieChart
                        height={310}
                        series={[
                            {
                                data: artistData,
                                innerRadius: 20,
                                outerRadius: 100,
                                paddingAngle: 2,
                            },
                        ]}
                        colors={COLORS}
                        legend={{ position: "bottom" }}
                        sx={{
                            '& .MuiChartsLegend-root, & .MuiChartsTooltip-root': {
                                color: 'var(--light-gray)', // legend and tooltip text
                            },
                        }}
                    />
                </section>

                <section className={styles.statBlock}>
                    <h3>Playlist Insights</h3>
                    <p>
                        <strong>Throwback Index:</strong> {stats.throwback_index}%{" "}
                        <small>(tracks &gt; 10 yr old)</small>
                    </p>
                    <p>
                        <strong>Explicit Energy:</strong> {stats.explicit_energy}%
                    </p>
                    <p>
                        <strong>Artist Concentration:</strong>{" "}
                        {stats.artist_concentration}%
                    </p>
                    <p>
                        <strong>Freshness Score:</strong> {stats.freshness_score}%
                    </p>
                    <p>
                        <strong>Collab Score:</strong> {stats.collab_score}
                    </p>
                </section>
            </div>

            <h2 className={styles.trackHeader}>Tracks</h2>
            <ul className={styles.trackList}>

                {stats.tracks.map((track) => (
                    <li className={styles.trackItem} key={track.id}>
                        <div>
                            <strong>{track.name}</strong>{" "}
                            <em>by {track.artists?.map(artist => artist.name).join(", ") || "Unknown"}</em>
                        </div>
                    </li>
                ))}

            </ul>
        </>
    );
}
