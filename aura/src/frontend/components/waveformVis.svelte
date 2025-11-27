<script>
    import { onMount } from "svelte";

    import { shiftB, dtwmethod, dtwOption } from "../stores";

    export let analysis = null;

    let canvas;
    let ctx;
    let selectedDTW = "dtw_own";

    let width = 0; //1500;
    let height = 0; //200;
    const margin = 20;

    let container;

    function applyShift(data, shift) {
        const shiftedData = [...data];
        if (shift > 0) {
            // Add zeros at the beginning and remove from the end
            return Array(shift).fill(0).concat(shiftedData.slice(0, -shift));
        } else if (shift < 0) {
            // Remove from the beginning and add zeros at the end
            return shiftedData.slice(-shift).concat(Array(-shift).fill(0));
        }
        return shiftedData;
    }

    function drawWaveform(waveform, duration, maxDuration, color, offsetY = 0) {
        if (!waveform || waveform.length === 0) return;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();

        const quotient = duration / maxDuration;

        const scaledWidth = Math.floor(quotient * width);

        for (let i = 0; i < waveform.length; i++) {
            const x = Math.floor((i / waveform.length) * scaledWidth); // Map each waveform entry to a pixel position
            const yVal = waveform[i];
            const y = offsetY + height / 2 - (yVal * height) / 2;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    function drawDTWOverlay(path, wlen1, len1, wlen2, len2, maxlen) {
        if (!path || path.length === 0) return;

        const scaledLen1 = len1 / maxlen;
        const scaledLen2 = len2 / maxlen;

        const xScale1 = width * scaledLen1;
        const xScale2 = width * scaledLen2;

        for (const point of path) {
            const i_sample = point.x / wlen1;
            const j_sample = (point.y + $shiftB) / wlen2;

            const x1 = i_sample * xScale1;
            const x2 = j_sample * xScale2;

            const y1 = margin + height / 2;
            const y2 = 2 * margin + height + height / 2;

            /*
            const deviation = Math.abs(x1 - x2);
            const maxDev = width / 5;
            const alpha = Math.max(0.2, 1 - Math.min(1, deviation / maxDev));
            */

            const hopSize = 28; // Assuming each hop corresponds to 512 samples in the MFCC analysis

            const hopDeviation = Math.abs(
                point.x / hopSize - (point.y + $shiftB) / hopSize,
            ); // measured in number of MFCC frames

            // Alpha increases by 0.2 per hop (cap at 1.0)
            const alpha = Math.min(1.0, 0.05 + 0.1 * hopDeviation);

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = `rgba(88, 88, 88, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }

    function drawOnsets(
        onsets,
        duration,
        maxDuration,
        offsetY = 0,
        color = "#888",
    ) {
        if (!onsets || onsets.length === 0) return;

        for (const t of onsets) {
            const x = (t / maxDuration) * width; // normalize by duration of the audio

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
        //let waveformB = analysis.features.waveform.fileB;
        let waveformB = applyShift(analysis.features.waveform.fileB, $shiftB);

        let dtw = analysis.dtw;
        let dtwPath = dtw[$dtwmethod];

        // 🔧 Compute global max for normalization
        const maxA = Math.max(...waveformA.map(Math.abs));
        const maxB = Math.max(...waveformB.map(Math.abs));
        let globalMax = Math.max(maxA, maxB);
        if (globalMax === 0) globalMax = 1; // avoid divide-by-zero

        waveformA = waveformA.map((v) => v / globalMax);
        waveformB = waveformB.map((v) => v / globalMax);

        const durationA = analysis.features.duration.fileA; // or: (mfccA.length * hopSize) / sampleRate;
        const durationB = analysis.features.duration.fileB;

        const maxDuration = Math.max(durationA, durationB);

        drawWaveform(waveformA, durationA, maxDuration, "#3498db", margin);
        drawWaveform(
            waveformB,
            durationB,
            maxDuration,
            "#e74c3c",
            height + margin * 2,
        );

        /*
        // Onset overlays
        drawOnsets(
            analysis.features.onsets.fileA,
            durationA,
            maxDuration,
            height + margin,
            "#2980b9",
        );
        drawOnsets(
            analysis.features.onsets.fileB,
            durationB,
            maxDuration,
            height + margin * 2,
            "#c0392b",
        );
        */

        drawDTWOverlay(
            dtwPath,
            waveformA.length,
            durationA,
            waveformB.length,
            durationB,
            maxDuration,
        );
    }

    /*
    $: if (analysis && ctx) {
        draw();
    }
    */

    $: shiftB.subscribe((shift) => {
        draw(); // Redraw the canvas whenever the shift changes
    });

    $: dtwmethod.subscribe(() => {
        if (ctx && analysis) {
            draw();
        }
    });

    onMount(() => {
        ctx = canvas.getContext("2d");

        // Use ResizeObserver to dynamically update width and height
        const resizeObserver = new ResizeObserver(() => {
            if (container) {
                width = Math.min(container.offsetWidth, window.innerWidth);
                height = container.offsetHeight / 2; // Adjust height as needed
                canvas.width = width;
                canvas.height = height * 2 + margin * 2;
                draw();
            }
        });

        resizeObserver.observe(container);

        if (analysis) {
            draw();
        }
    });
</script>

<div bind:this={container} class="canvas-container">
    <h3>Waveform Comparison</h3>
    <label>
        Blue = {analysis ? analysis?.files[0] : "fileA"}, Red = {analysis
            ? analysis?.files[1]
            : "fileB"}
    </label>

    <canvas bind:this={canvas}></canvas>
</div>

<style>
    .canvas-container {
        width: 100%; /* Take full width of the parent grid item */
        height: 100%; /* Take full height of the parent grid item */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

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
