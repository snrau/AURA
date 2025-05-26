<script>
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";

    export let analysis = null;

    let canvasRMS;
    let canvasPitch;
    let canvasCentroid;

    let chartRMS, chartPitch, chartCentroid;

    function createLineChart(ctx, label, data, color) {
        return new Chart(ctx, {
            type: "line",
            data: {
                labels: data.map((_, i) => i),
                datasets: [
                    {
                        label,
                        data,
                        borderColor: color,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true } },
                scales: {
                    x: { display: false },
                    y: { beginAtZero: true },
                },
            },
        });
    }

    function destroyCharts() {
        chartRMS?.destroy();
        chartPitch?.destroy();
        chartCentroid?.destroy();
    }

    $: if (analysis) {
        // Clean up existing charts before redraw
        destroyCharts();

        // Audio 1 features
        const rms1 = analysis.audio_1.rms || [];
        const pitch1 = analysis.audio_1.pitch || [];
        const centroid1 = analysis.audio_1.centroid || [];

        // Audio 2 features
        const rms2 = analysis.audio_2.rms || [];
        const pitch2 = analysis.audio_2.pitch || [];
        const centroid2 = analysis.audio_2.centroid || [];

        // Create charts with two datasets (Audio 1 = blue, Audio 2 = red)
        chartRMS = new Chart(canvasRMS.getContext("2d"), {
            type: "line",
            data: {
                labels: rms1.map((_, i) => i),
                datasets: [
                    {
                        label: "RMS Audio 1",
                        data: rms1,
                        borderColor: "#3498db",
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                    },
                    {
                        label: "RMS Audio 2",
                        data: rms2,
                        borderColor: "#e74c3c",
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true } },
                scales: {
                    x: { display: false },
                    y: { beginAtZero: true },
                },
            },
        });

        chartPitch = createLineChart(
            canvasPitch.getContext("2d"),
            "Pitch Audio 1",
            pitch1,
            "#3498db",
        );
        chartPitch.data.datasets.push({
            label: "Pitch Audio 2",
            data: pitch2,
            borderColor: "#e74c3c",
            fill: false,
            tension: 0.1,
            pointRadius: 0,
        });
        chartPitch.update();

        chartCentroid = createLineChart(
            canvasCentroid.getContext("2d"),
            "Spectral Centroid Audio 1",
            centroid1,
            "#3498db",
        );
        chartCentroid.data.datasets.push({
            label: "Spectral Centroid Audio 2",
            data: centroid2,
            borderColor: "#e74c3c",
            fill: false,
            tension: 0.1,
            pointRadius: 0,
        });
        chartCentroid.update();
    }
</script>

<div>
    <h3>Feature Charts</h3>

    <div>
        <canvas bind:this={canvasRMS} width="700" height="150"></canvas>
    </div>

    <div>
        <canvas bind:this={canvasPitch} width="700" height="150"></canvas>
    </div>

    <div>
        <canvas bind:this={canvasCentroid} width="700" height="150"></canvas>
    </div>
</div>

<style>
    h3 {
        margin-bottom: 0.5rem;
    }
    canvas {
        background: #fafafa;
        border: 1px solid #ccc;
        margin-bottom: 1rem;
    }
</style>
