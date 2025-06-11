<script>
    import { onMount } from "svelte";

    export let onsetsA = [];
    export let onsetsB = [];
    export let onsetStrengthA = [];
    export let onsetStrengthB = [];
    export let durationA = 1; // Prevent divide by zero
    export let durationB = 1; // Prevent divide by zero

    let canvas;
    let ctx;

    const width = 1500;
    const height = 150;
    const radius = 4;

    function drawOnsetDots(onsets, y, color) {
        ctx.fillStyle = color;
        for (const t of onsets) {
            const x = (t / durationA) * width;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawOnsetStrength(strength, color, duration, offsetY, maxVal) {
        if (!strength.length) return;

        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;

        //const maxVal = Math.max(...strength);
        strength.forEach((val, i) => {
            const t = (i / strength.length) * duration;
            const x = (t / duration) * width;
            const y = offsetY - (val / maxVal) * (height * 0.17); // scale into chart height
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    }

    function drawOverlayStrength(
        strengthA,
        strengthB,
        duration,
        offsetY,
        maxVal,
    ) {
        const minLen = Math.min(strengthA.length, strengthB.length);
        if (minLen === 0) return;

        ctx.beginPath();
        ctx.strokeStyle = "#2ecc71"; // green for overlap
        ctx.lineWidth = 1.2;

        const differences = Array.from(
            { length: minLen },
            (_, i) => strengthA[i] - strengthB[i], //Math.abs(),
        );
        //const maxVal = Math.max(...differences);

        differences.forEach((val, i) => {
            const t = (i / minLen) * duration;
            const x = (t / duration) * width;
            const y = offsetY - (val / maxVal) * (height * 0.17);
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    }

    function draw() {
        if (!ctx) return;
        ctx.clearRect(0, 0, width, height);

        const yA = height * 0.25;
        const yB = height * 0.87;
        const yOverlay = height * 0.52;

        const maxVal = Math.max(...onsetStrengthA, ...onsetStrengthB);
        drawOnsetStrength(onsetStrengthA, "#3498db", durationA, yA, maxVal);
        drawOnsetStrength(onsetStrengthB, "#e74c3c", durationB, yB, maxVal);
        drawOverlayStrength(
            onsetStrengthA,
            onsetStrengthB,
            Math.max(durationA, durationB),
            yOverlay,
            maxVal,
        );

        drawOnsetDots(onsetsA, yA, "#3498db");
        drawOnsetDots(onsetsB, yB, "#e74c3c");
    }

    $: if (ctx) draw();

    onMount(() => {
        ctx = canvas.getContext("2d");
        draw();
    });
</script>

<div>
    <h3>Onset Comparison</h3>
    <canvas bind:this={canvas} {width} {height}></canvas>
</div>

<style>
    canvas {
        border: 1px solid #ccc;
        background: #fff;
        display: block;
        margin-bottom: 1rem;
    }

    h3 {
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
</style>
