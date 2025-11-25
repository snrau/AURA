<script>
    import { onMount } from "svelte";
    import {
        scaleLinear,
        interpolateBlues,
        interpolateRdBu,
        interpolateViridis,
    } from "d3";
    import { shiftB } from "../stores";

    export let matrix = [[]]; // 2D array of values
    export let title = "";
    export let maxValue = 1; // for scaling colors
    export let cellSize = 3; // pixels per cell
    export let gap = 0; // gap between cells
    export let lengthB = 1;

    let canvas;
    let ctx;

    let shiftedMatrix = [...matrix]; // Local copy of the shifted matrix

    let zoomLevel = 1; // Zoom level (1 = full matrix, >1 = zoomed in)
    let visibleRows = matrix.length; // Number of visible rows
    let visibleCols = matrix[0].length; // Number of visible columns
    let offsetRow = 0; // Starting row for the viewport
    let offsetCol = 0; // Starting column for the viewport

    let debounceTimeout; // Timeout for debouncing

    let colorScale = scaleLinear()
        .domain([-maxValue, 0, maxValue]) // input range
        .range([0, 0.5, 1]); // normalized to 0–1 for the interpolator

    function getColor(value) {
        // Normalize value between 0 and 1
        const t = Math.max(0, Math.min(1, colorScale(value)));
        return interpolateViridis(t);
    }

    function applyShiftToMatrix(matrix, shift, matrixLength, waveformLength) {
        // Scale the shift to match the resolution of the matrix
        const scaledShift = Math.round((shift / waveformLength) * matrixLength);

        if (scaledShift > 0) {
            // Add rows of zeros at the top and remove rows from the bottom
            const emptyRow = Array(matrix[0].length).fill(0);
            for (let i = 0; i < scaledShift; i++) {
                shiftedMatrix.unshift(emptyRow); // Add a row of zeros at the top
            }
            shiftedMatrix.splice(-scaledShift); // Remove rows from the bottom
        } else if (scaledShift < 0) {
            // Remove rows from the top and add rows of zeros at the bottom
            const emptyRow = Array(matrix[0].length).fill(0);
            shiftedMatrix.splice(0, -scaledShift); // Remove rows from the top
            for (let i = 0; i < -scaledShift; i++) {
                shiftedMatrix.push(emptyRow); // Add a row of zeros at the bottom
            }
        }

        return shiftedMatrix;
    }

    function drawMatrix() {
        if (!ctx || !shiftedMatrix.length || !shiftedMatrix[0].length) return;

        ctx.clearRect(0, 0, canvas?.width, canvas?.height);

        for (let row = 0; row < shiftedMatrix.length; row++) {
            for (let col = 0; col < shiftedMatrix[row].length; col++) {
                const value = shiftedMatrix[row][col];
                ctx.fillStyle = getColor(value);
                const x = col * (cellSize + gap);
                const y = (shiftedMatrix.length - 1 - row) * (cellSize + gap);
                ctx.fillRect(x, y, cellSize, cellSize);
            }
        }
    }

    function zoomIn() {
        if (cellSize < 10) {
            cellSize += 1;
            updateViewport();
        }
    }

    function zoomOut() {
        if (cellSize > 1) {
            cellSize -= 1;
            updateViewport();
        }
    }

    function updateViewport() {
        canvas.width = visibleCols * (cellSize + gap) - gap;
        canvas.height = visibleRows * (cellSize + gap) - gap;

        drawMatrix();
    }

    // Subscribe to the shiftB store and update the shifted matrix
    $: shiftB.subscribe((shift) => {
        clearTimeout(debounceTimeout); // Clear the previous timeout
        debounceTimeout = setTimeout(() => {
            shiftedMatrix = applyShiftToMatrix(
                matrix,
                shift,
                matrix.length,
                lengthB,
            );
            drawMatrix(); // Redraw the matrix after the debounce delay
        }, 300); // 300ms debounce delay
    });

    $: if (ctx) drawMatrix();

    onMount(() => {
        ctx = canvas.getContext("2d");
        updateViewport();
    });
</script>

<div>
    <h3>{title} {matrix?.length} x {matrix[0].length}</h3>
    <button on:click={zoomIn}>Zoom In</button>
    <button on:click={zoomOut}>Zoom Out</button>
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
