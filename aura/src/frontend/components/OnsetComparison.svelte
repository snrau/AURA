<script>
    import { onMount } from "svelte";

    export let fileAname = ""
    export let fileBname = ""
    export let onsetsA = [];
    export let onsetsB = [];
    export let onsetStrengthA = [];
    export let onsetStrengthB = [];
    export let durationA = 1; // Prevent divide by zero
    export let durationB = 1; // Prevent divide by zero
    export let lengthB = 1;
    export let shift

    let canvas;
    let ctx;

    let width = 0; //1500;
    let height = 0; //150;
    const radius = 4;

    let container;

    let shiftedOnsetsB = [...onsetsB]; // Local copy of shifted onsets
    let shiftedOnsetStrengthB = [...onsetStrengthB]; // Local copy of shifted onset strengths

    function calculateTimeShift(shiftB, waveformLength, waveformDuration) {
        return (shiftB / waveformLength) * waveformDuration; // Time shift in seconds
    }

    // Subscribe to the shiftB store and update the shifted data
    $: if(shift !== undefined) forceShift(shift)

    $: if (ctx && (fileAname || fileBname)) {
        forceShift(shift ?? 0);
    }

    function forceShift(shift){
        console.log("forceShift", shift)
        let shiftTime = calculateTimeShift(shift, lengthB, durationB);
        shiftedOnsetsB = applyTimeShiftToOnsets(onsetsB, shiftTime);
        shiftedOnsetStrengthB = applyShiftToStrength(
            onsetStrengthB,
            shift,
            onsetStrengthB.length,
            lengthB,
        );
        draw();
    }

    // Function to shift onset times
    function applyTimeShiftToOnsets(onsets, timeShift) {
        return onsets.map((t) => t + timeShift).filter((t) => t >= 0); // Keep only valid timestamps
    }

    function applyShiftToStrength(
        strength,
        shift,
        strengthLength,
        waveformLength,
    ) {
        const scaledShift = Math.round(
            (shift / waveformLength) * strengthLength,
        );

        const shiftedStrength = [...strength];
        if (scaledShift > 0) {
            return Array(scaledShift)
                .fill(0)
                .concat(shiftedStrength.slice(0, -scaledShift));
        } else if (scaledShift < 0) {
            return shiftedStrength
                .slice(-scaledShift)
                .concat(Array(-scaledShift).fill(0));
        }
        return shiftedStrength;
    }

    function drawOnsetDots(onsets, duration, y, color) {
        ctx.fillStyle = color;
        for (const t of onsets) {
            const x = (t / duration) * width;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawOnsetStrength(
        strength,
        color,
        duration,
        maxDuration,
        offsetY,
        maxVal,
    ) {
        if (!strength.length) return;

        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;

        //const maxVal = Math.max(...strength);
        strength.forEach((val, i) => {
            const t = (i / strength.length) * duration;
            const x = (t / maxDuration) * width;
            const y = offsetY - (val / maxVal) * (height * 0.17); // scale into chart height
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    }

    function drawOverlayStrength(strengthA, strengthB, offsetY, maxVal) {
        const minLen = Math.min(strengthA.length, strengthB.length);
        if (minLen === 0) return;

        ctx.beginPath();
        ctx.strokeStyle = "#2ecc71"; // green for overlap
        ctx.lineWidth = 1.2;

        const differences = Array.from(
            { length: Math.max(strengthA.length, strengthB.length) },
            (_, i) => (strengthA[i] ?? 0) - (strengthB[i] ?? 0), //Math.abs(),
        );
        //const maxVal = Math.max(...differences);

        differences.forEach((val, i) => {
            const x = (i / differences.length) * width;
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

        const maxLength = Math.max(durationA, durationB);

        const maxVal = Math.max(...onsetStrengthA, ...onsetStrengthB);
        drawOnsetStrength(
            onsetStrengthA,
            "#3498db",
            durationA,
            maxLength,
            yA,
            maxVal,
        );
        drawOnsetStrength(
            shiftedOnsetStrengthB,
            "#e74c3c",
            durationB,
            maxLength,
            yB,
            maxVal,
        );
        drawOverlayStrength(
            onsetStrengthA,
            shiftedOnsetStrengthB,
            yOverlay,
            maxVal,
        );

        drawOnsetDots(onsetsA, maxLength, yA, "#3498db");
        drawOnsetDots(shiftedOnsetsB, maxLength, yB, "#e74c3c");
    }

    onMount(() => {
        ctx = canvas.getContext("2d");

        // Use ResizeObserver to dynamically update width and height
        const resizeObserver = new ResizeObserver(() => {
            if (container) {
                width = Math.min(container.offsetWidth, window.innerWidth);
                height = container.offsetHeight;
                canvas.width = width;
                canvas.height = height;
                forceShift(0)
            }
        });

        resizeObserver.observe(container);
        forceShift(0)
    });
</script>

<div bind:this={container} class="canvas-container">
    <h3>Onset Comparison</h3>
    <canvas bind:this={canvas} {width} {height}></canvas>
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
        background: #fff;
        display: block;
        margin-bottom: 1rem;
    }

    h3 {
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
</style>
