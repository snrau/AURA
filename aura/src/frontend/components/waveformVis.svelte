<script>
    import { onMount } from "svelte";

    export let analysis = null; // The full JSON data with audio_1, audio_2, dtw_path

    let canvas;
    let ctx;

    // Dimensions
    const width = 700;
    const height = 200;
    const margin = 20;

    // Utility: normalize array to [-1, 1]
    function normalize(arr) {
        const maxVal = Math.max(...arr.map(Math.abs));
        if (maxVal === 0) return arr;
        return arr.map((v) => v / maxVal);
    }

    // Draw waveform on canvas context
    function drawWaveform(waveform, color, offsetY = 0) {
        if (!waveform || waveform.length === 0) return;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        const norm = normalize(waveform);
        const step = Math.ceil(norm.length / width);

        for (let x = 0; x < width; x++) {
            const slice = norm.slice(x * step, (x + 1) * step);
            if (slice.length === 0) break;
            const yVal = slice.reduce((a, b) => a + b, 0) / slice.length;
            const y = offsetY + height / 2 - yVal * (height / 2 - margin);
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    // Draw overlay highlighting DTW differences
    function drawDTWOverlay() {
        if (!analysis) return;

        const path = analysis.dtw_path;
        if (!path || path.length === 0) return;

        ctx.strokeStyle = "rgba(255, 0, 0, 0.4)";
        ctx.lineWidth = 2;
        ctx.beginPath();

        // Map DTW indices to x coords on canvas
        // Assume waveform length corresponds roughly to number of samples
        const len1 = analysis.audio_1.waveform.length;
        const len2 = analysis.audio_2.waveform.length;

        const xScale1 = width / len1;
        const xScale2 = width / len2;

        for (let i = 0; i < path.length; i++) {
            const p = path[i];
            const x1 = p.x * xScale1;
            const x2 = p.y * xScale2;
            const y1 = height / 2;
            const y2 = height + height / 2;

            // Draw line connecting corresponding points on waveform1 & waveform2
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
        }
        ctx.stroke();
    }

    // Draw everything
    function draw() {
        if (!ctx || !analysis) return;
        ctx.clearRect(0, 0, width, height * 2 + margin * 2);

        // Draw first waveform on top
        drawWaveform(analysis.audio_1.waveform, "#3498db", margin);

        // Draw second waveform below
        drawWaveform(analysis.audio_2.waveform, "#e74c3c", height + margin * 2);

        // Overlay DTW alignment lines
        drawDTWOverlay();
    }

    // Run draw on mount and when analysis changes
    $: if (analysis) {
        draw();
    }

    onMount(() => {
        ctx = canvas.getContext("2d");
    });
</script>

<div>
    <h3>Waveforms Overlay (Blue = Audio 1, Red = Audio 2)</h3>
    <canvas bind:this={canvas} {width} height={height * 2 + margin * 2}
    ></canvas>
</div>

<style>
    canvas {
        border: 1px solid #ccc;
        background: #fafafa;
        display: block;
        margin-bottom: 1rem;
    }

    h3 {
        margin: 0.5rem 0;
    }
</style>
