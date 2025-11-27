<script>
    import { onMount } from "svelte";
    import axios from "axios";
    import WaveformVisualizer from "./components/waveformVis.svelte";
    import LineChart from "./components/LineChart.svelte";
    import OnsetComparison from "./components/OnsetComparison.svelte";
    import MatrixChart from "./components/MatrixChart.svelte";
    import { dtwmethod, dtwOption, shiftB } from "./stores";

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
    let showRMS = true;
    let showSpectralCentroid = true;
    let showVibrato = true;
    let showF0Framewise = true;
    let showMatrix = true;

    $: visibleVisualizations =
        (showWaveform ? 1 : 0) +
        (showF0 ? 1 : 0) +
        (showRMS ? 1 : 0) +
        (showSpectralCentroid ? 1 : 0) +
        (showVibrato ? 1 : 0) +
        (showMatrix ? 1 : 0);

    onMount(async () => {
        await loadResultsList();
    });

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
        if (files.length === 0) {
            errorMsg = "Please select one or two audio files.";
            return;
        }
        if (files.length !== 2) {
            errorMsg = "Please upload exactly two audio files for comparison.";
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
    </div>

    {#if uploadResult}
        <div class="grid">
            {#if showWaveform}
                <div class="grid-item waveform">
                    <label for="dtwSelect">DTW Method:</label>
                    <select id="dtwSelect" bind:value={$dtwmethod}>
                        {#each dtwOption as method}
                            <option value={method}>{method}</option>
                        {/each}
                    </select>
                    <label for="shiftB">Shift File B:</label>
                    <input
                        id="shiftB"
                        type="range"
                        min="-200"
                        max="200"
                        bind:value={$shiftB}
                    />
                    <span
                        on:click={() => {
                            shiftB.set(0);
                        }}>{$shiftB} samples</span
                    >
                    <WaveformVisualizer analysis={uploadResult} />
                </div>
            {/if}

            {#if showOnsetComparison}
                <div class="grid-item waveform">
                    <OnsetComparison
                        onsetsA={uploadResult.features.onsets.fileA}
                        onsetsB={uploadResult.features.onsets.fileB}
                        onsetStrengthA={uploadResult.features.onsets_strength
                            .fileA}
                        onsetStrengthB={uploadResult.features.onsets_strength
                            .fileB}
                        durationA={uploadResult.features.duration.fileA}
                        durationB={uploadResult.features.duration.fileB}
                        lengthB={uploadResult.features.length.fileB}
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
                        valuesA={uploadResult.features.f0.fileA}
                        valuesB={uploadResult.features.f0.fileB}
                        files={uploadResult.files}
                        lengthB={uploadResult.features.length.fileB}
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
                        valuesA={uploadResult.features.rms.fileA}
                        valuesB={uploadResult.features.rms.fileB}
                        files={uploadResult.files}
                        lengthB={uploadResult.features.length.fileB}
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
                        valuesA={uploadResult.features.spectral_centroid.fileA}
                        valuesB={uploadResult.features.spectral_centroid.fileB}
                        files={uploadResult.files}
                        lengthB={uploadResult.features.length.fileB}
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
                        valuesA={uploadResult.features.vibrato.fileA}
                        valuesB={uploadResult.features.vibrato.fileB}
                        files={uploadResult.files}
                        lengthB={uploadResult.features.length.fileB}
                    />
                </div>
            {/if}

            {#if showMatrix}
                <div class="grid-item other-visualizations">
                    <MatrixChart
                        title="Similarity"
                        matrix={uploadResult.similarity}
                        lengthB={uploadResult.features.length.fileB}
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
</style>
