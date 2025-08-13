<script>
    import { onMount } from "svelte";
    import { scaleLinear, interpolateBlues } from "d3";

    export let matrix = [[]]; // 2D array of values
    export let title = ""
    export let maxValue = 1; // for scaling colors
    export let cellSize = 1; // pixels per cell
    export let gap = 0; // gap between cells

    let canvas;
    let ctx;

    let colorScale = scaleLinear()
        .domain([0.3, maxValue])       // input range
        .range([0, 1])               // normalized to 0–1 for the interpolator

    function getColor(value) {
        // Normalize value between 0 and 1
        const t = Math.max(0, Math.min(1, colorScale(value)));
        return interpolateBlues(t);
    }

    function drawMatrix() {
        if (!ctx || !matrix.length || !matrix[0].length) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let row = 0; row < matrix.length; row++) {
            for (let col = 0; col < matrix[row].length; col++) {
                const value = matrix[row][col];
                ctx.fillStyle = getColor(value);
                const x = col * (cellSize + gap);
                const y = row * (cellSize + gap);
                ctx.fillRect(x, y, cellSize, cellSize);
            }
        }
    }

    $: if (ctx) drawMatrix();

    onMount(() => {
        ctx = canvas.getContext("2d");
        canvas.width = matrix[0].length * (cellSize + gap) - gap;
        canvas.height = matrix.length * (cellSize + gap) - gap;
        drawMatrix();
    });
</script>

<div>
    <h3>{title}p</h3>
    <canvas bind:this={canvas}></canvas>
</div>

<style>
    canvas {
        border: 1px solid #ccc;
        background: #fff;
        display: block;
    }
    h3 {
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
</style>