<script>
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";

    export let title = "Line Chart";
    export let valuesA = [];
    export let valuesB = [];
    export let files = [];

    let canvas;
    let chart;

    onMount(() => {
        if (chart) chart.destroy();

        chart = new Chart(canvas, {
            type: "line",
            data: {
                labels: valuesA.map((_, i) => i), // x-axis: index/frame
                datasets: [
                    {
                        label: files[0],
                        data: valuesA,
                        borderColor: "rgba(54, 162, 235, 1)",
                        backgroundColor: "rgba(54, 162, 235, 0.2)",
                        fill: false,
                        tension: 0.2,
                    },
                    {
                        label: files[1],
                        data: valuesB,
                        borderColor: "rgba(255, 99, 132, 1)",
                        backgroundColor: "rgba(255, 99, 132, 0.2)",
                        fill: false,
                        tension: 0.2,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 18,
                        },
                    },
                    legend: {
                        position: "top",
                    },
                },
                scales: {
                    x: {
                        display: false,
                        title: {
                            display: false,
                            text: "Frame Index",
                        },
                    },
                    y: {
                        display: false,
                        title: {
                            display: false,
                            text: title,
                        },
                    },
                },
                layout: {
                    padding: 0, // optional: removes any default padding
                },
            },
        });
    });
</script>

<canvas bind:this={canvas}></canvas>
