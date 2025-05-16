<script>
    export let features = []; // Each: { name: "pitch", values: [...] }
    export let single = true;

    function normalize(values) {
        const max = Math.max(...values);
        return values.map((v) => v / max);
    }
    console.log(single);

    const colors = ["#1e90ff", "#ff6347", "#32cd32", "#ffa500", "#8a2be2"];
</script>

<h2>Feature Viewer</h2>

{#each features as feature}
    <div>
        <h3>{feature.name}</h3>
        <svg width="600" height="100">
            {#if single === true}
                <polyline
                    fill="none"
                    stroke={feature.name === "pitch" ? "green" : "#1e90ff"}
                    stroke-width="1"
                    points={normalize(feature.values)
                        .map((val, i) => `${i},${100 - val * 100}`)
                        .join(" ")}
                />
            {:else}
                {#each normalize(feature.values) as series, i}
                    <polyline
                        fill="none"
                        stroke={colors[i % colors.length]}
                        stroke-width="1"
                        points={series
                            .map((v, j) => `${j},${100 - v * 100}`)
                            .join(" ")}
                    />
                {/each}
            {/if}
        </svg>
    </div>
{/each}
