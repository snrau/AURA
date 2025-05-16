<script>
    export let path = []; // Array of [i, j]
</script>

<h2>DTW Alignment Path</h2>
<svg width="300" height="300">
    <line x1="0" y1="0" x2="300" y2="300" stroke="#ccc" />
    {#each path as [i, j]}
        <circle cx={i} cy={j} r="1" fill="red" />
    {/each}
</svg>
