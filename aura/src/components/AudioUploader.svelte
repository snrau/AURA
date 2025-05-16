<script>
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    function handleFiles(event) {
        const files = Array.from(event.target.files);
        dispatch("upload", { files });
    }
</script>

<h2>Upload Guitar Takes</h2>
<input type="file" multiple accept="audio/*" on:change={handleFiles} />
