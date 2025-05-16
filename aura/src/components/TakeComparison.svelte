<script>
    export let distanceMatrix = []; // 2D array
</script>

<h2>Take Comparison (Distance Matrix)</h2>
<table border="1">
    <tr>
        <th></th>
        {#each distanceMatrix as _, j}
            <th>Take {j + 1}</th>
        {/each}
    </tr>
    {#each distanceMatrix as row, i}
        <tr>
            <td><strong>Take {i + 1}</strong></td>
            {#each row as cell}
                <td
                    >{cell.euclidean.toFixed(3)} / {cell?.dtwCost.toFixed(3)}
                </td>
            {/each}
        </tr>
    {/each}
</table>
