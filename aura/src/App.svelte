<script>
	import AudioUploader from "./components/AudioUploader.svelte";
	import FeatureViewer from "./components/FeatureViewer.svelte";
	import TakeComparison from "./components/TakeComparison.svelte";

	import { extractFeaturesFromBuffer } from "./lib/audioFeatures.js";
	import { computeDetailedDistanceMatrix } from "./lib/similarity.js";
	import { alignAllTakes } from "./lib/alignment.js";

	let featuresList = [];
	let alignedFeatures = [];
	let distanceMatrix = [];

	async function handleUpload(event) {
		console.log("Files uploaded:", event.detail.files);
		const files = event.detail.files;
		const ctx = new AudioContext();
		featuresList = [];

		for (let file of files) {
			const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
			console.log("Decoded audio buffer:", buffer);
			const features = await extractFeaturesFromBuffer(ctx, buffer);
			console.log("Extracted features:", features);
			featuresList.push(features);
		}

		if (featuresList.length > 1) {
			alignedFeatures = alignAllTakes(featuresList);
			console.log("Aligned features:", alignedFeatures);
		}

		distanceMatrix = computeDetailedDistanceMatrix(
			alignedFeatures.map((f) => f.mfcc),
		);
		console.log("Distance matrix:", distanceMatrix);
	}
</script>

<AudioUploader on:upload={handleUpload} />

{#if alignedFeatures.length}
	<FeatureViewer
		features={[
			{ name: "Pitch", values: alignedFeatures.map((f) => f.pitch) },
			{ name: "RMS", values: alignedFeatures.map((f) => f.rms) },
		]}
		single={false}
	/>
	<TakeComparison {distanceMatrix} />
{:else if featuresList.length}
	<FeatureViewer
		features={[
			{ name: "RMS", values: featuresList[0].rms },
			{ name: "Pitch", values: featuresList[0].pitch },
		]}
		single={true}
	/>
	<TakeComparison {distanceMatrix} />
{/if}
