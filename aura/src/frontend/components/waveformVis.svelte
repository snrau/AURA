<script>
    import { onMount } from "svelte";

    export let analysis = null;

    let canvas;
    let ctx;
    let selectedDTW = "dtw_own";
    let dtwOption = ["dtw_mfcc", "dtw_own", "dtw_chroma", "dtw_mixed"];

    const width = 1500;
    const height = 200;
    const margin = 20;

    function drawWaveform(waveform, color, offsetY = 0) {
        if (!waveform || waveform.length === 0) return;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();

        const step = Math.max(1, Math.floor(waveform.length / width));

        for (let x = 0; x < width; x++) {
            const slice = waveform.slice(x * step, (x + 1) * step);
            if (slice.length === 0) break;
            const yVal = slice.reduce((a, b) => a + b, 0) / slice.length;
            const y = offsetY + height / 2 - yVal * height;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    function drawDTWOverlay(path, len1, len2) {
        if (!path || path.length === 0) return;

        const scaledLen1 = len1;
        const scaledLen2 = len2;

        const xScale1 = width / scaledLen1;
        const xScale2 = width / scaledLen2;

        for (const point of path) {
            const i_sample = point.x;
            const j_sample = point.y;

            const x1 = i_sample * xScale1;
            const x2 = j_sample * xScale2;

            const y1 = margin + height / 2;
            const y2 = 2 * margin + height + height / 2;

            /*
            const deviation = Math.abs(x1 - x2);
            const maxDev = width / 5;
            const alpha = Math.max(0.2, 1 - Math.min(1, deviation / maxDev));
            */

            const hopSize = 512; // Assuming each hop corresponds to 512 samples in the MFCC analysis

            const hopDeviation = Math.abs(
                i_sample / hopSize - j_sample / hopSize,
            ); // measured in number of MFCC frames

            // Alpha increases by 0.2 per hop (cap at 1.0)
            const alpha = Math.min(1.0, 0.1 + 0.2 * hopDeviation);

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = `rgba(88, 88, 88, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }

    function drawOnsets(onsets, duration, offsetY = 0, color = "#888") {
        if (!onsets || onsets.length === 0) return;

        for (const t of onsets) {
            const x = (t / duration) * width; // normalize by duration of the audio

            /*ctx.beginPath();
            ctx.moveTo(x, offsetY);
            ctx.lineTo(x, offsetY + margin);
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.stroke();
            */

            ctx.beginPath();
            ctx.fillStyle = color;
            ctx.arc(x, offsetY + margin / 2, margin / 2, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function draw() {
        if (!ctx || !analysis || !analysis.features) return;
        ctx.clearRect(0, 0, width, height * 2 + margin * 2);

        let waveformA = analysis.features.waveform.fileA;
        let waveformB = analysis.features.waveform.fileB;

        let dtw = analysis.dtw;
        let dtwPath = dtw[selectedDTW];

        // 🔧 Compute global max for normalization
        const maxA = Math.max(...waveformA.map(Math.abs));
        const maxB = Math.max(...waveformB.map(Math.abs));
        let globalMax = Math.max(maxA, maxB);
        if (globalMax === 0) globalMax = 1; // avoid divide-by-zero

        waveformA = waveformA.map((v) => v / globalMax);
        waveformB = waveformB.map((v) => v / globalMax);

        drawWaveform(waveformA, "#3498db", margin);
        drawWaveform(waveformB, "#e74c3c", height + margin * 2);

        const durationA = waveformA.length / 22050; // or: (mfccA.length * hopSize) / sampleRate;
        const durationB = waveformB.length / 22050;

        console.log(durationA, durationB);

        // Onset overlays
        drawOnsets(
            analysis.features.onsets.fileA,
            durationA,
            height + margin,
            "#2980b9",
        );
        drawOnsets(
            analysis.features.onsets.fileB,
            durationB,
            height + margin * 2,
            "#c0392b",
        );

        drawDTWOverlay(dtwPath, waveformA.length, waveformB.length);
    }

    /*
    $: if (analysis && ctx) {
        draw();
    }
    */

    $: selectedDTW,
        () => {
            if (ctx && analysis) {
                draw();
            }
        };

    onMount(() => {
        ctx = canvas.getContext("2d");
        if (analysis) {
            draw();
        }
    });
</script>

<div>
    <h3>Waveform Comparison</h3>
    <h5>
        Blue = {analysis ? analysis?.files[0] : "fileA"}, Red = {analysis
            ? analysis?.files[1]
            : "fileB"}
    </h5>

    <label for="dtwSelect">DTW Method:</label>
    <select id="dtwSelect" bind:value={selectedDTW} on:change={draw}>
        {#each dtwOption as method}
            <option value={method}>{method}</option>
        {/each}
    </select>

    <canvas bind:this={canvas} {width} height={height * 2 + margin * 2}
    ></canvas>
</div>

<style>
    canvas {
        border: 1px solid #ccc;
        background: #f8f8f8;
        display: block;
        margin-bottom: 1rem;
    }
    h3 {
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
</style>
