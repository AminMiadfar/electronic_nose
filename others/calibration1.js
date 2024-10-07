// JS File: static/js/calibration.js
window.onload = function() {
    // Radar chart logic
    const ctx = document.getElementById('radarChart').getContext('2d');

    const cleanAirData = JSON.parse(document.getElementById('cleanAirData').textContent);
    const calibrationData = JSON.parse(document.getElementById('calibrationData').textContent);

    const radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['MQ2', 'MQ3', 'MQ4', 'MQ6', 'MQ7', 'MQ135'], // Adjust labels based on sensors
            datasets: [
                {
                    label: 'Clean Air',
                    data: cleanAirData, // Clean air criteria data
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                },
                {
                    label: 'Calibration Data',
                    data: calibrationData, // Calibration capture data
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                }
            ]
        },
        options: {
            scale: {
                ticks: { beginAtZero: true }
            }
        }
    });
};
