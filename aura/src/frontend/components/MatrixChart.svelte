<script>
    import { onMount } from "svelte";
    import { scaleLinear, interpolateBlues, interpolateRdBu } from "d3";
    import { shiftB } from "../stores";

    export let matrix = [[]]; // 2D array of values
    export let title = "";
    export let maxValue = 1; // for scaling colors
    export let cellSize = 1; // pixels per cell
    export let gap = 0; // gap between cells
    export let lengthB = 1;

    let canvas;
    let ctx;

    let shiftedMatrix = [...matrix]; // Local copy of the shifted matrix

    let colorScale = scaleLinear()
        .domain([-maxValue, 0, maxValue]) // input range
        .range([0, 0.5, 1]); // normalized to 0–1 for the interpolator

    function getColor(value) {
        // Normalize value between 0 and 1
        const t = Math.max(0, Math.min(1, colorScale(value)));
        return interpolateRdBu(t);
    }

    function applyShiftToMatrix(matrix, shift, matrixLength, waveformLength) {
        // Scale the shift to match the resolution of the matrix
        const scaledShift = Math.round((shift / waveformLength) * matrixLength);

        const shiftedMatrix = matrix.map((row) => {
            if (scaledShift > 0) {
                // Add zeros at the beginning and remove from the end
                return Array(scaledShift)
                    .fill(0)
                    .concat(row.slice(0, -scaledShift));
            } else if (scaledShift < 0) {
                // Remove from the beginning and add zeros at the end
                return row
                    .slice(-scaledShift)
                    .concat(Array(-scaledShift).fill(0));
            }
            return row;
        });

        return shiftedMatrix;
    }

    function drawMatrix() {
        if (!ctx || !matrix.length || !matrix[0].length) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let row = 0; row < matrix.length; row++) {
            for (let col = 0; col < matrix[row].length; col++) {
                const value = matrix[row][col];
                ctx.fillStyle = getColor(value);
                const x = col * (cellSize + gap);
                const y = (matrix.length - 1 - row) * (cellSize + gap);
                ctx.fillRect(x, y, cellSize, cellSize);
            }
        }
    }

    // Subscribe to the shiftB store and update the shifted matrix
    $: shiftB.subscribe((shift) => {
        shiftedMatrix = applyShiftToMatrix(
            matrix,
            shift,
            matrix[0].length,
            lengthB,
        );
        drawMatrix(); // Redraw the matrix whenever the shift changes
    });

    $: if (ctx) drawMatrix();

    onMount(() => {
        ctx = canvas.getContext("2d");
        canvas.width = matrix[0].length * (cellSize + gap) - gap;
        canvas.height = matrix.length * (cellSize + gap) - gap;
        console.log(matrix.length);
        drawMatrix();
    });
</script>

<div>
    <h3>{title} {matrix?.length} x {matrix[0].length}</h3>
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
