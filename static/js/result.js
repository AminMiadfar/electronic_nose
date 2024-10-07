document.addEventListener('DOMContentLoaded', function () {
    // Retrieve data from data attributes
    const sensorAverages = JSON.parse(document.getElementById('sensor-data').dataset.sensors);
    const calibrationAverages = JSON.parse(document.getElementById('calibration-data').dataset.calibration);
    const labels = ['MQ2', 'MQ3', 'MQ4', 'MQ6', 'MQ7', 'MQ135'];

    // Data for the sensor and calibration radar chart
    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Sensor Averages',
                data: sensorAverages,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
            },
            {
                label: 'Calibration Averages',
                data: calibrationAverages,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
            },
        ],
    };

    // Configuration for the sensor and calibration radar chart
    const config = {
        type: 'radar',
        data: data,
        options: {
            elements: {
                line: {
                    tension: 0.1 // Smooth line
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    pointLabels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            },
        },
    };

    // Create the radar chart for sensor and calibration averages
    const radarChart = new Chart(
        document.getElementById('radarChart'),
        config
    );

    // Retrieve temperature and humidity data
    const temperature = parseFloat(document.getElementById('temperature-humidity').dataset.temp);
    const humidity = parseFloat(document.getElementById('temperature-humidity').dataset.humidity);

    // Data for the temperature and humidity bar chart
    const barData = {
        labels: ['Temperature (°C)', 'Humidity (%)'],
        datasets: [{
            label: 'Temperature and Humidity',
            data: [temperature, humidity],
            backgroundColor: [
                'rgba(255, 206, 86, 0.2)', // Yellow for Temperature
                'rgba(75, 192, 192, 0.2)', // Teal for Humidity
            ],
            borderColor: [
                'rgba(255, 206, 86, 1)', // Yellow
                'rgba(75, 192, 192, 1)', // Teal
            ],
            borderWidth: 1
        }]
    };

    const barConfig = {
        type: 'bar',
        data: barData,
        options: {
            scales: {
                x: {
                    ticks: {
                        font: {
                            size: 14,
                            weight: 'bold' // Bold for x-axis labels
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 14,
                            weight: 'bold' // Bold for y-axis labels
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold' // Bold legend labels
                        }
                    }
                }
            },
            // Adjust the appearance of the bars
            elements: {
                bar: {
                    backgroundColor: [
                        'rgba(255, 99, 71, 0.7)', // Bright Red for Temperature
                        'rgba(0, 128, 255, 0.7)',  // Bright Blue for Humidity
                    ],
                    borderColor: [
                        'rgba(255, 69, 0, 1)', // Darker Red for Temperature
                        'rgba(0, 0, 255, 1)',  // Darker Blue for Humidity
                    ],
                    borderWidth: 2, // Thicker borders for more contrast
                    borderRadius: 5, // Round the corners of the bars
                    barThickness: 40 // Thicker bars for more visibility
                }
            }
        }
    };
    

    // Create the bar chart for temperature and humidity
    const barChart = new Chart(
        document.getElementById('barChart'),
        barConfig
    );

    // Data for the wine characteristics radar chart
    const characteristics = JSON.parse(document.getElementById('characteristics-data').dataset.characteristics);
    const characteristicsLabels = ['Dry', 'Sweet', 'Light', 'Bold', 'Soft', 'Tannic', 'Acidic', 'Smooth'];
    const characteristicsValues = characteristicsLabels.map(label => parseFloat(characteristics[label.toLowerCase()]));

    const characteristicsData = {
        labels: characteristicsLabels,
        datasets: [{
            label: 'Wine Characteristics',
            data: characteristicsValues,
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1,
        }],
    };

    // Configuration for the wine characteristics radar chart
    const characteristicsConfig = {
        type: 'radar',
        data: characteristicsData,
        options: {
            elements: {
                line: {
                    tension: 0.1 // Smooth line
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    pointLabels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            },
        },
    };

    // Create the radar chart for wine characteristics
    const characteristicsRadarChart = new Chart(
        document.getElementById('characteristicsRadarChart'),
        characteristicsConfig
    );
});
