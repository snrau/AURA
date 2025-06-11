<script>
    import { onMount } from "svelte";
    import axios from "axios";
    import WaveformVisualizer from "./components/waveformVis.svelte";
    import LineChart from "./components/LineChart.svelte";
    import OnsetComparison from "./components/OnsetComparison.svelte";

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
                headers: { "Content-Type": "multipart/form-data" },
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
            loadedResult = res.data;
            uploadResult = null; // Clear upload result view if any
        } catch (err) {
            console.error("Failed to load result file:", err);
            errorMsg = "Failed to load result file";
        }
    }
</script>

<main>
    <h1>🎙️ Audio Comparison Tool</h1>

    <section>
        <h2>Upload Two Audio Files</h2>
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

    <section style="margin-top: 2rem;">
        <h2>Or Load Previous Analysis</h2>
        <select bind:value={selectedFile}>
            <option disabled value="">-- Select a JSON file --</option>
            {#each resultFiles as file}
                <option>{file}</option>
            {/each}
        </select>
        <button on:click={loadResultFile}>Load Result</button>
    </section>

    <section style="margin-top: 2rem;">
        {#if uploadResult}
            <WaveformVisualizer analysis={uploadResult} />
            <!--<FeatureCharts analysis={loadedResult.features} />
            <MFCCHeatmap analysis={loadedResult.features} />-->
            <OnsetComparison
                onsetsA={uploadResult.features.onsets.fileA}
                onsetsB={uploadResult.features.onsets.fileB}
                onsetStrengthA={uploadResult.features.onsets_strength.fileA}
                onsetStrengthB={uploadResult.features.onsets_strength.fileB}
                durationA={uploadResult.features.duration.fileA}
                durationB={uploadResult.features.duration.fileB}
            />
            <LineChart
                title="F0"
                valuesA={uploadResult.features.f0.fileA}
                valuesB={uploadResult.features.f0.fileB}
                files={uploadResult.files}
            />
            <LineChart
                title="RMS"
                valuesA={uploadResult.features.rms.fileA}
                valuesB={uploadResult.features.rms.fileB}
                files={uploadResult.files}
            />
            <LineChart
                title="Spectral Centroid"
                valuesA={uploadResult.features.spectral_centroid.fileA}
                valuesB={uploadResult.features.spectral_centroid.fileB}
                files={uploadResult.files}
            />
            <LineChart
                title="Vibrato"
                valuesA={uploadResult.features.vibrato.fileA}
                valuesB={uploadResult.features.vibrato.fileB}
                files={uploadResult.files}
            />
            <LineChart
                title="F0 Framewise"
                valuesA={uploadResult.features.f0_framewise.fileA}
                valuesB={uploadResult.features.f0_framewise.fileB}
                files={uploadResult.files}
            />
        {/if}
        {#if loadedResult}
            <WaveformVisualizer analysis={loadedResult} />
            <!--<FeatureCharts analysis={loadedResult.features} />
            <MFCCHeatmap analysis={loadedResult.features} />-->
            <OnsetComparison
                onsetsA={loadedResult.features.onsets.fileA}
                onsetsB={loadedResult.features.onsets.fileB}
                onsetStrengthA={loadedResult.features.onsets_strength.fileA}
                onsetStrengthB={loadedResult.features.onsets_strength.fileB}
                durationA={loadedResult.features.duration.fileA}
                durationB={loadedResult.features.duration.fileB}
            />
            <LineChart
                title="F0"
                valuesA={loadedResult.features.f0.fileA}
                valuesB={loadedResult.features.f0.fileB}
                files={loadedResult.files}
            />
            <LineChart
                title="RMS"
                valuesA={loadedResult.features.rms.fileA}
                valuesB={loadedResult.features.rms.fileB}
                files={loadedResult.files}
            />
            <LineChart
                title="Spectral Centroid"
                valuesA={loadedResult.features.spectral_centroid.fileA}
                valuesB={loadedResult.features.spectral_centroid.fileB}
                files={loadedResult.files}
            />
            <LineChart
                title="Vibrato"
                valuesA={loadedResult.features.vibrato.fileA}
                valuesB={loadedResult.features.vibrato.fileB}
                files={loadedResult.files}
            />
            <LineChart
                title="F0 Framewise"
                valuesA={loadedResult.features.f0_framewise.fileA}
                valuesB={loadedResult.features.f0_framewise.fileB}
                files={loadedResult.files}
            />
        {/if}
    </section>
</main>

<style>
    main {
        margin: 2rem auto;
        font-family: sans-serif;
    }

    section {
        width: 1500px;
    }

    input[type="file"] {
        margin-top: 0.5rem;
    }

    button {
        margin-left: 1rem;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }

    select {
        margin-top: 0.5rem;
        padding: 0.5rem;
        font-size: 1rem;
    }

    pre {
        background: #f4f4f4;
        padding: 1rem;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
        max-height: 400px;
    }
</style>
