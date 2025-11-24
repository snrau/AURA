<script>
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";
    import { shiftB } from "../stores";

    export let title = "Line Chart";
    export let valuesA = [];
    export let valuesB = [];
    export let files = [];
    export let lengthB = [];

    let canvas;
    let chart;

    let shiftedValuesB = [...valuesB];

    // Subscribe to the shiftB store and update the shifted values
    $: shiftB.subscribe((shift) => {
        shiftedValuesB = applyShift(valuesB, shift, valuesB.length, lengthB);
        updateChart(); // Update the chart whenever the shift changes
    });

    // Function to apply the shift to the data
    function applyShift(data, shift, dataLength, lengthB) {
        // Scale the shift to match the resolution of the dataset
        const scaledShift = Math.round((shift / lengthB) * dataLength);

        const shiftedData = [...data];
        if (scaledShift > 0) {
            // Add zeros at the beginning and remove from the end
            return Array(scaledShift)
                .fill(0)
                .concat(shiftedData.slice(0, -scaledShift));
        } else if (scaledShift < 0) {
            // Remove from the beginning and add zeros at the end
            return shiftedData
                .slice(-scaledShift)
                .concat(Array(-scaledShift).fill(0));
        }
        return shiftedData;
    }

    // Function to update the chart dynamically
    function updateChart() {
        if (chart) {
            chart.data.datasets[0].data = valuesA; // Update File A data
            chart.data.datasets[1].data = shiftedValuesB; // Update shifted File B data
            chart.update(); // Redraw the chart
        }
    }

    onMount(() => {
        if (chart) chart.destroy();

        length = Math.max(valuesA.length, shiftedValuesB.length);

        chart = new Chart(canvas, {
            type: "line",
            data: {
                labels: Array.from(Array(length).keys()), // x-axis: index/frame
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
                        data: shiftedValuesB,
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
