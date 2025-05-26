<script>
    import { onMount } from "svelte";

    export let analysis = null;

    let canvas;
    const width = 700;
    const height = 200;

    // Map MFCC values to colors (simple grayscale)
    function valueToColor(val, min, max) {
        const norm = (val - min) / (max - min + 1e-6);
        const shade = Math.floor(255 * (1 - norm));
        return `rgb(${shade},${shade},${shade})`;
    }

    function drawHeatmap(mfcc) {
        if (!canvas || !mfcc) return;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, width, height);

        const nCoeffs = mfcc.length;
        if (nCoeffs === 0) return;

        const nFrames = mfcc[0].length;

        // Find global min/max for scaling color
        let minVal = Infinity;
        let maxVal = -Infinity;
        for (let i = 0; i < nCoeffs; i++) {
            for (let j = 0; j < nFrames; j++) {
                const v = mfcc[i][j];
                if (v < minVal) minVal = v;
                if (v > maxVal) maxVal = v;
            }
        }

        const cellWidth = width / nFrames;
        const cellHeight = height / nCoeffs;

        for (let i = 0; i < nCoeffs; i++) {
            for (let j = 0; j < nFrames; j++) {
                const val = mfcc[i][j];
                ctx.fillStyle = valueToColor(val, minVal, maxVal);
                ctx.fillRect(
                    j * cellWidth,
                    i * cellHeight,
                    cellWidth,
                    cellHeight,
                );
            }
        }
    }

    $: if (analysis && analysis.audio_1?.mfcc) {
        drawHeatmap(analysis.audio_1.mfcc);
    }
</script>

<h3>MFCC Heatmap (Audio 1)</h3>
<canvas bind:this={canvas} {width} {height} style="border:1px solid #ccc;"
></canvas>
