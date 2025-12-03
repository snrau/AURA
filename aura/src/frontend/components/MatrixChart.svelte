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
    export let shift

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

    function applyShiftToMatrix(originalMatrix, shift, waveformLength) {
        // Scale the shift to match the resolution of the matrix
        const rows = originalMatrix.length;
        const cols = originalMatrix[0].length;
        const scaledShift = Math.round((shift / waveformLength) * cols);

        if (scaledShift === 0) {
            return originalMatrix.map(r => [...r]);
        }
        const newMatrix = []
        

        for (let r = 0; r < rows; r++) {
            if (scaledShift > 0) {
            // SHIFT DOWN → zeros at TOP
            if (r < scaledShift) {
                // new top rows filled with zeros
                newMatrix.push(Array(cols).fill(0));
            } else {
                // take row from above (shifted position)
                newMatrix.push([...originalMatrix[r - scaledShift]]);
            }
        }

        else if (scaledShift < 0) {
            // SHIFT UP → zeros at BOTTOM
            const up = -scaledShift;

            if (r >= rows - up) {
                // new bottom rows filled with zeros
                newMatrix.push(Array(cols).fill(0));
            } else {
                // take row from below (shifted position)
                newMatrix.push([...originalMatrix[r + up]]);
            }
        }
        }

        return newMatrix;
    }

    function drawMatrix() {
        if (!ctx || !shiftedMatrix.length || !shiftedMatrix[0].length) return;

        ctx.clearRect(0, 0, canvas?.width, canvas?.height);

        for (let row = 0; row < shiftedMatrix.length; row++) {
            for (let col = 0; col < shiftedMatrix[row].length; col++) {
                const value = shiftedMatrix[row][col];
                ctx.fillStyle = row === col ? "grey" : getColor(value);
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
    $: if(shift !== undefined) {
        clearTimeout(debounceTimeout); // Clear the previous timeout
        debounceTimeout = setTimeout(() => {
            shiftedMatrix = applyShiftToMatrix(
                matrix,
                shift,
                lengthB,
            );
            drawMatrix(); // Redraw the matrix after the debounce delay
        }, 300); // 300ms debounce delay
    };

    $: if (ctx) drawMatrix();

    onMount(() => {
        ctx = canvas.getContext("2d");
        updateViewport();
    });
</script>

<div>
    <h3>{title} {matrix?.length} x {matrix[0].length}</h3>
    <button on:click={zoomIn}>Bigger</button>
    <button on:click={zoomOut}>Smaller</button>
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
