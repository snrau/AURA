<script>
    import { onMount } from "svelte";
    import axios from "axios";
    import WaveformVisualizer from "./components/waveformVis.svelte";
    import LineChart from "./components/LineChart.svelte";
    import OnsetComparison from "./components/OnsetComparison.svelte";
    import MatrixChart from "./components/MatrixChart.svelte";
    import { dtwmethod, dtwOption, shiftB, shiftStore  } from "./stores";
    import MatrixGlyph from "./components/MatrixGlyph.svelte";

    // Backend base URL
    const BASE_URL = "http://localhost:8000";

    // State
    let files = [];
    let uploadResult = null;
    let isUploading = false;
    let errorMsg = "";

    // For loading saved results from backend
    let resultFiles = [];
    let selectedFile = "";
    let loadedResult = null;

    // Visibility toggles for each section
    let showWaveform = true;
    let showOnsetComparison = true;
    let showF0 = true;
    let showDiff = true;
    let showRMS = true;
    let showSpectralCentroid = true;
    let showVibrato = true;
    let showF0Framewise = true;
    let showMatrix = true;

    $: visibleVisualizations =
        (showWaveform ? 1 : 0) +
        (showF0 ? 1 : 0) +
        (showDiff ? 1 : 0) +
        (showRMS ? 1 : 0) +
        (showSpectralCentroid ? 1 : 0) +
        (showVibrato ? 1 : 0) +
        (showMatrix ? 1 : 0);

    let selectedPairKey = "";
    let availablePairs = [];

    // Build pair keys dynamically
    $: if (uploadResult?.comparisons) {
        availablePairs = Object.keys(uploadResult.comparisons).sort();
        if (!selectedPairKey && availablePairs.length > 0) {
            selectedPairKey = availablePairs[0];
        }
    }

    // Convenience getters
    $: [file1Id, file2Id] = selectedPairKey ? selectedPairKey.split("") : ["", ""];
    $: selectedPairData = uploadResult?.comparisons?.[selectedPairKey] ?? null;
    $: file1 = uploadResult?.files?.find(f => f.id === file1Id);
    $: file2 = uploadResult?.files?.find(f => f.id === file2Id);

    onMount(async () => {
        await loadResultsList();
    });

    let previousPairKey = null;
    let currentShift = 0;

    $: if (selectedPairKey && selectedPairKey !== previousPairKey) {
        previousPairKey = selectedPairKey;
        // load stored shift for new pair
        currentShift = $shiftStore[selectedPairKey] ?? 0;
    }

    function updateShift(val) {
        shiftStore.setShift(selectedPairKey, +val);
    }

    function resetShift() {
        currentShift = 0
        shiftStore.resetShift(selectedPairKey);
    }

    async function loadResultsList() {
        try {
            const res = await axios.get(`${BASE_URL}/results`);
            resultFiles = res.data.results;
        } catch (err) {
            console.error("Error loading results list", err);
        }
    }

    async function uploadFiles() {
        errorMsg = "";
        if (files.length < 2) {
            errorMsg = "Please select two or more audio files.";
            return;
        }
        if (files.length > 10) {
            errorMsg = "Please upload up to 10 audio files for comparison.";
            return;
        }

        isUploading = true;
        uploadResult = null;
        loadedResult = null;

        const formData = new FormData();
        for (const file of files) {
            formData.append("files", file);
        }

        try {
            const res = await axios.post(`${BASE_URL}/upload`, formData, {
                headers: {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "multipart/form-data",
                },
            });
            uploadResult = res.data;

            // Refresh the results list to include the new JSON file
            await loadResultsList();
        } catch (err) {
            console.error("Upload failed:", err);
            errorMsg = "Upload failed, see console.";
        } finally {
            isUploading = false;
        }
    }

    async function loadResultFile() {
        if (!selectedFile) return;

        try {
            const res = await axios.get(`${BASE_URL}/results/${selectedFile}`);
            console.log("Loaded result file:", res.data);
            //loadedResult = res.data;
            uploadResult = null; // Clear upload result view if any
            uploadResult = res.data;
        } catch (err) {
            console.error("Failed to load result file:", err);
            errorMsg = "Failed to load result file";
        }
    }
</script>

<main>
    <header>
        <h2>🎙️ AURA</h2>
        <div class="options">
            <section>
                <label> Upload Audio Files</label>
                <input
                    type="file"
                    multiple
                    accept="audio/*"
                    on:change={(e) => (files = e.target.files)}
                />
                <button on:click={uploadFiles} disabled={isUploading}>
                    {isUploading ? "Uploading..." : "Upload & Analyze"}
                </button>

                {#if errorMsg}
                    <p style="color: red;">{errorMsg}</p>
                {/if}
            </section>

            <section>
                <label> Or Load Analysis</label>
                <select bind:value={selectedFile}>
                    <option disabled value="">-- Select a JSON file --</option>
                    {#each resultFiles as file}
                        <option>{file}</option>
                    {/each}
                </select>
                <button on:click={loadResultFile}>Load Result</button>
            </section>
        </div>
    </header>

    <!-- Show/Hide Buttons -->
    <div class="toggle-bar">
        <button on:click={() => (showWaveform = !showWaveform)}>
            {showWaveform ? "Hide Waveform" : "Show Waveform"}
        </button>
        <button on:click={() => (showOnsetComparison = !showOnsetComparison)}>
            {showOnsetComparison
                ? "Hide Onset Comparison"
                : "Show Onset Comparison"}
        </button>
        <button on:click={() => (showDiff = !showDiff)}>
            {showDiff ? "Hide Diff" : "Show Diff"}
        </button>
        <button on:click={() => (showF0 = !showF0)}>
            {showF0 ? "Hide F0" : "Show F0"}
        </button>
        <button on:click={() => (showRMS = !showRMS)}>
            {showRMS ? "Hide RMS" : "Show RMS"}
        </button>
        <button on:click={() => (showSpectralCentroid = !showSpectralCentroid)}>
            {showSpectralCentroid
                ? "Hide Spectral Centroid"
                : "Show Spectral Centroid"}
        </button>
        <button on:click={() => (showVibrato = !showVibrato)}>
            {showVibrato ? "Hide Vibrato" : "Show Vibrato"}
        </button>
        <button on:click={() => (showMatrix = !showMatrix)}>
            {showMatrix ? "Hide Matrix" : "Show Matrix"}
        </button>
         <!-- Pair selector integrated in toggle bar -->
        <div class="pair-select">
            <label for="pairSelect">Compare:</label>
            <select id="pairSelect" bind:value={selectedPairKey}>
                {#each availablePairs as pairKey}
                    {#if uploadResult.comparisons[pairKey]}
                        <option value={pairKey}>
                            {pairKey} ({uploadResult.files.find(f => f.id === pairKey[0])?.name} vs {uploadResult.files.find(f => f.id === pairKey[1])?.name})
                        </option>
                    {/if}
                {/each}
            </select>
        </div>
        {#if selectedPairKey}
        <div class="pair-shift-control">
            <label for="shift">Shift File {selectedPairKey[1]}:</label>
            <button class="shift-btn" on:click={() => {currentShift--; updateShift(currentShift)}}>
                −
            </button>
            <input
                id="shift"
                type="range"
                min="-200"
                max="200"
                bind:value={currentShift}
                on:input={(e) => updateShift(e.target.value)}
            />
            <button class="shift-btn" on:click={() => {currentShift++; updateShift(currentShift)}}>
                +
            </button>
            <span on:click={resetShift}>
                {currentShift} samples
            </span>
        </div>
        {/if}
    </div>

    {#if uploadResult && file1 && file2}
        <div class="grid">
            {#if showWaveform}
                <div class="grid-item waveform">
                    <label for="dtwSelect">DTW Method:</label>
                    <select id="dtwSelect" bind:value={$dtwmethod}>
                        {#each dtwOption as method}
                            <option value={method}>{method}</option>
                        {/each}
                    </select>
                    <WaveformVisualizer fileA={file1.features} fileB={file2.features} dtw={selectedPairData.dtw} shift={currentShift}/>
                </div>
            {/if}

            {#if showOnsetComparison}
                <div class="grid-item waveform">
                    <OnsetComparison
                        fileAname={file1.name}
                        fileBname={file2.name}
                        onsetsA={file1.features.onsets}
                        onsetsB={file2.features.onsets}
                        onsetStrengthA={file1.features.onsets_strength}
                        onsetStrengthB={file2.features.onsets_strength}
                        durationA={file1.features.duration}
                        durationB={file2.features.duration}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}

            {#if showDiff}
                <div
                    class="grid-item line-chart"
                    style="grid-column: {visibleVisualizations <= 4
                        ? 'span 2'
                        : 'span 1'}"
                >
                    <MatrixGlyph
                        title="F0 - this needs to be split into two files 1 and 2"
                        fileA={file1.features} 
                        fileB={file2.features}
                        shift={currentShift}

                    />
                </div>
            {/if}

            {#if showF0}
                <div
                    class="grid-item line-chart"
                    style="grid-column: {visibleVisualizations <= 4
                        ? 'span 2'
                        : 'span 1'}"
                >
                    <LineChart
                        title="F0"
                        valuesA={file1.features.f0}
                        valuesB={file2.features.f0}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}

            {#if showRMS}
                <div
                    class="grid-item line-chart"
                    style="grid-column: {visibleVisualizations <= 4
                        ? 'span 2'
                        : 'span 1'}"
                >
                    <LineChart
                        title="RMS"
                        valuesA={file1.features.rms}
                        valuesB={file2.features.rms}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}

            {#if showSpectralCentroid}
                <div
                    class="grid-item line-chart"
                    style="grid-column: {visibleVisualizations <= 4
                        ? 'span 2'
                        : 'span 1'}"
                >
                    <LineChart
                        title="Spectral Centroid"
                        valuesA={file1.features.spectral_centroid}
                        valuesB={file2.features.spectral_centroid}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}

            {#if showVibrato}
                <div
                    class="grid-item line-chart"
                    style="grid-column: {visibleVisualizations <= 4
                        ? 'span 2'
                        : 'span 1'}"
                >
                    <LineChart
                        title="Vibrato"
                        valuesA={file1.features.vibrato}
                        valuesB={file2.features.vibrato}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}

            {#if showMatrix}
                <div class="grid-item other-visualizations">
                    <MatrixChart
                        title="Similarity"
                        matrix={selectedPairData.similarity}
                        lengthB={file2.features.length}
                        shift={currentShift}
                    />
                </div>
            {/if}
        </div>
    {/if}
</main>

<style>
    main {
        margin: 0;
        padding: 0;
        font-family: sans-serif;
        display: grid;
        grid-template-rows: auto 1fr;
        height: 100vh;
    }

    .options {
        display: flex;
        align-items: center;
        gap: 2rem;
    }

    header {
        position: fixed;
        top: 0;
        left: 0;
        width: 98%;
        height: 60px;
        background-color: #333;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        z-index: 1000;
    }

    header h2 {
        font-size: 1.2rem;
        margin: 0;
        white-space: nowrap;
    }

    .toggle-bar {
        position: relative;
        top: 28px; /* Push the toggle bar below the header */
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        background-color: #444;
        color: white;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        z-index: 999; /* Ensure it appears above other content */
    }

    .toggle-bar button {
        font-size: 0.9rem;
        padding: 5px 10px;
        background-color: #555;
        color: white;
        border: none;
        border-radius: 3px;
        cursor: pointer;
    }

    .toggle-bar button:hover {
        background-color: #666;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 2 columns */
        grid-template-rows: repeat(4, 1fr); /* 4 rows */
        gap: 20px;
        margin-top: 120px; /* Leave space for the fixed header and toggle bar */
        padding: 20px;
    }

    .grid-item {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .waveform {
        grid-column: 1 / span 2; /* Span both columns */
        grid-row: auto; /* Take 1 row */
        height: 300px; /* Larger height for the waveform */
    }

    /* Line charts are smaller and stacked vertically */
    .line-chart {
        height: 150px; /* Smaller height for line charts */
    }

    .matrix {
        height: 200px; /* Fixed height for the matrix */
    }

    .pair-select {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    }

    .pair-select select {
        padding: 0.2rem 0.4rem;
    }
    .shift-btn {
        width: 32px;
        height: 28px;
        font-size: 18px;
        font-weight: 600;
        border: 1px solid #ccc;
        background: #f5f5f5;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.15s;
        user-select: none;
    }
</style>
