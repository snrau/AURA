<script>
    import { onMount } from "svelte";
    import {
        scaleLinear,
        interpolateReds,
        interpolateRdBu,
        interpolateViridis,
    } from "d3";

    export let fileA;
    export let fileB;
    export let title = "Comparison Glyph";
    export let cellSize = 4;
    export let gap = 1;
    export let timeCells = 100; // width of the glyph
    export let shift

    let canvas;
    let ctx;

    // List the features you want to visualize — max ~7 for readability
    const possibleFeatures = [
        "f0",
        "rms",
        "spectral_centroid",
        "onsets_strength",
        "onsets",
        "chroma_cens",
    ];

    // Only include features that exist in the analysis object
    let featureList = [];
    let differenceMatrix = [[]];
    let shiftedMatrix = [[]];


    let debounceTimeout; // Timeout for debouncing

    // Utility: compute the average of items in an array
    function avg(arr) {
        if (arr.length === 0) return 0;
        return arr.reduce((a, b) => a + b, 0) / arr.length;
    }

    /**
     * Rescale a feature array (with known duration) into a fixed number of timeCells.
     * Each output cell aggregates all samples that fall into the time window.
     */
     function scaleFeatureToTimeline(values, featureName, durationSeconds, cellCount) {
        if (!values || values.length === 0) return Array(cellCount).fill(3000);


        if (featureName === "onsets") {
            const result = Array(cellCount).fill(0);

            for (const onsetTime of values) {
                const percentage = onsetTime / durationSeconds; // 0–1
                const cellIndex = Math.floor(percentage * cellCount);

                if (cellIndex >= 0 && cellIndex < cellCount) {
                    result[cellIndex] = 1; // mark onset
                }
            }
            return result;
        }

        const cellSize = durationSeconds / cellCount;
        const timestamps = values.map((_, i) => (i / values.length) * durationSeconds);

        const result = [];

        for (let c = 0; c < cellCount; c++) {
            const start = c * cellSize;
            const end = start + cellSize;

            const bucket = [];

            for (let i = 0; i < values.length; i++) {
                if (timestamps[i] >= start && timestamps[i] < end) {
                    bucket.push(values[i]);
                }
            }

            result.push(avg(bucket));
        }

        return result;
    }

    function scaleOnsetsToTimeline(onsets, durationSeconds, cellCount) {
    const cellSize = durationSeconds / cellCount;
    const result = Array(cellCount).fill(0);

    for (let t of onsets) {
        const cellIndex = Math.floor(t / cellSize);
        if (cellIndex >= 0 && cellIndex < cellCount) {
            result[cellIndex] = 1; // mark onset
        }
    }

    return result;
}

    function shiftArrayBySamples(array, shift, lengthB) {
    if (!array || !array.length) return [];

    const N = array.length;

    // Scale the shift to the array length
    const scaledShift = Math.round((shift / lengthB) * N);

    if (scaledShift === 0) return [...array];

    let shifted = [];

    if (scaledShift > 0) {
        // shift right → add zeros at start
        shifted = Array(scaledShift).fill(0).concat(array);
        shifted = shifted.slice(0, N); // trim to original length
    } else {
        // shift left → add zeros at end
        shifted = array.slice(-scaledShift).concat(Array(-scaledShift).fill(0));
    }

    return shifted;
    
}

function shift2DMatrixBySamples(matrix, shift, lengthB) {
    const rows = matrix.length;
    const cols = matrix[0].length;

    const scaledShift = Math.round((shift / lengthB) * cols);
    if (scaledShift === 0) return matrix.map(r => [...r]);

    const newMatrix = [];

    for (let r = 0; r < rows; r++) {
        const row = [...matrix[r]];

        if (scaledShift > 0) {
            // shift right → zeros at start
            newMatrix.push(Array(scaledShift).fill(0).concat(row).slice(0, cols));
        } else {
            // shift left → zeros at end
            newMatrix.push(row.slice(-scaledShift).concat(Array(-scaledShift).fill(0)));
        }
    }

    return newMatrix;
}

function shiftOnsets(onsets, shiftSamples, totalSamples, durationSeconds) {
    if (!onsets) return [];

    // Convert sample shift → seconds
    const shiftSeconds = (shiftSamples / totalSamples) * durationSeconds;

    // Apply shift and clamp to [0, duration]
    return onsets
        .map(t => t + shiftSeconds)
        .filter(t => t >= 0 && t <= durationSeconds);
}


    function compare2DMatrices(A, B, durationA, durationB, timeCells) {
    const rows = A.length; // assume same rows for B
    const colsA = A[0].length;
    const colsB = B[0].length;

    // Generate timestamps for A and B
    const timestampsA = Array.from({ length: colsA }, (_, i) => (i / colsA) * durationA);
    const timestampsB = Array.from({ length: colsB }, (_, i) => (i / colsB) * durationB);

    const cellSize = Math.max(durationA, durationB) / timeCells;
    const result = [];

    for (let c = 0; c < timeCells; c++) {
        const start = c * cellSize;
        const end = start + cellSize;

        // Get indices in this time cell for A and B
        const indicesA = timestampsA.map((t, i) => (t >= start && t < end ? i : -1)).filter(i => i >= 0);
        const indicesB = timestampsB.map((t, i) => (t >= start && t < end ? i : -1)).filter(i => i >= 0);

        const values = [];

        // Compare each bin
        for (let r = 0; r < rows; r++) {
            // all pairs of time samples in this cell (A vs B)
            for (let i of indicesA) {
                for (let j of indicesB) {
                    const diff = Math.abs(A[r][i] - B[r][j]);
                    values.push(diff);
                }
            }
        }

        // Reduce to single scalar per time cell
        result.push(avg(values));
    }

    return result;
}

     /**
     * Compute normalized difference rows for all features.
     * Uses time-scaled versions of A and B so duration differences are handled correctly.
     */
     function computeDifferenceMatrix(shift) {
        differenceMatrix = [];

        const durationA = fileA.duration;
        const durationB = fileB.duration;
        const lengthB = fileB.waveform.length;

        for (let feature of featureList) {
            const A_raw = fileA[feature];
            let B_raw = fileB[feature];

            if (!A_raw || !B_raw) continue;

            let diffRow 
            if (feature === "onsets") {

                // 1. Shift timestamps
                const B_shifted = shiftOnsets(B_raw, shift, lengthB, durationB);

                // 2. Scale onsets to 100 cells
                const A_scaled = scaleOnsetsToTimeline(A_raw, durationA, timeCells);
                const B_scaled = scaleOnsetsToTimeline(B_shifted, durationB, timeCells);

                // 3. Compare per cell
                diffRow = A_scaled.map((a, i) => Math.abs(a - B_scaled[i]));

                }
            else if(feature === "chroma_cens" || feature === "mfcc"){
                B_raw = shift2DMatrixBySamples(B_raw, shift, lengthB);
                diffRow = compare2DMatrices(A_raw, B_raw, durationA, durationB, timeCells);
            }else{
                B_raw = shiftArrayBySamples(B_raw, shift, lengthB);
                // Scale both into the same number of time cells
                const A_scaled = scaleFeatureToTimeline(A_raw, feature, durationA, timeCells);
                const B_scaled = scaleFeatureToTimeline(B_raw, feature, durationB, timeCells);


                diffRow = A_scaled.map(
                    (a, i) => Math.abs(a - (B_scaled[i] ?? 3000))
                );
                
            }
            const maxVal = Math.max(...diffRow) || 1;
            differenceMatrix.push(diffRow.map(v => v / maxVal));
            
        }
        shiftedMatrix = differenceMatrix.map(row => [...row]);
    }

    let colorScale = scaleLinear()
        .domain([0, 1]) // input range
        .range([0, 1]); // normalized to 0–1 for the interpolator

    function getColor(value) {
        if(value === 3000) return "blue"
        // Normalize value between 0 and 1
        const t = Math.max(0, Math.min(1, Math.abs(value)));
        return interpolateReds(t);
    }


    function draw() {
        if (!ctx || shiftedMatrix.length === 0) return;

        const rows = shiftedMatrix.length;
        const cols = shiftedMatrix[0].length;

        canvas.width = cols * (cellSize + gap) - gap;
        canvas.height = rows * (cellSize + gap) - gap;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                ctx.fillStyle = getColor(shiftedMatrix[r][c]);

                const x = c * (cellSize + gap);
                const y = r * (cellSize + gap);

                ctx.fillRect(x, y, cellSize, cellSize);
            }
        }
    }


    $: if (fileA && fileB) {
        // build dynamic feature list
        featureList = possibleFeatures.filter(f =>
            fileA[f] &&
            fileB[f]
        );
        
        computeDifferenceMatrix(shift);
        draw();
    }

    $: shift, () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            computeDifferenceMatrix(shift);
            draw();
        }, 300);
    };

    onMount(() => {
        ctx = canvas.getContext("2d");
    });
    
</script>

<div>
    <h3>{title}</h3>

    <p>Comparing {featureList.length} features over {timeCells} time cells.</p>

    <canvas bind:this={canvas}></canvas>
</div>

<style>
    canvas {
        border: 1px solid #ccc;
        background: #fff;
        display: block;
        margin-top: 10px;
    }
</style>
