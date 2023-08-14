window.onload = function() {
    // Fetch the game result data and draw the charts
    fetch("/game1/get_result_data", {
        method: "GET",
    })
    .then(response => response.json())
    .then(data => {
        drawCharts(data.log);
        renderTable(data.log);
    })
    .catch(error => {
        console.error("Error:", error);
    });
};

// Variables for charts
let combinedChart;
let activityHoursChart;

function drawCharts(logData) {
    const ageData = Array.from({ length: logData.length }, (_, index) => 18 + index);
    const healthData = logData.map(entry => entry.health);
    const foodData = logData.map(entry => entry.food);
    const huntingHoursData = logData.map(entry => entry.hunting_hours).slice(1);
    const restingHoursData = logData.map(entry => entry.resting_hours).slice(1);

    // Destroy existing charts if they exist
    if (combinedChart) {
        combinedChart.destroy();
    }
    if (activityHoursChart) {
        activityHoursChart.destroy();
    }

    const combinedChartCanvas = document.getElementById("combined-chart").getContext("2d");
    const activityHoursChartCanvas = document.getElementById("activity-hours-chart").getContext("2d");

    combinedChart = new Chart(combinedChartCanvas, {
        type: "line",
        data: {
            labels: ageData,
            datasets: [
                {
                    label: "Health",
                    data: healthData,
                    borderColor: "#007bff",
                    fill: false
                },
                {
                    label: "Food",
                    data: foodData,
                    borderColor: "#28a745",
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: "Health and Food Status Over Time"
                },
                legend: {
                    position: "bottom"
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    activityHoursChart = new Chart(activityHoursChartCanvas, {
        type: "bar",
        data: {
            labels: ageData.slice(1),
            datasets: [
                {
                    label: "Resting Hours",
                    data: restingHoursData,
                    backgroundColor: "#007bff"
                },
                {
                    label: "Hunting Hours",
                    data: huntingHoursData,
                    backgroundColor: "#28a745"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: "Activity Hours Over Time"
                },
                legend: {
                    position: "bottom"
                }
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }],
                xAxes: [{
                    offset: true
                }]
            }
        }
    });

    // Show the charts and start over button after the game is over
    if (gameOver) {
        document.querySelector(".chart-container").style.display = "block";
        document.getElementById("restart-button").style.display = "block";
    } else {
        document.querySelector(".chart-container").style.display = "none";
        document.getElementById("restart-button").style.display = "none";
    }
}

function renderTable(logData) {
    // Code to render the table
    const gameLog = document.getElementById("game-log").getElementsByTagName('tbody')[0];
    logData.forEach(logEntry => {
        const newRow = gameLog.insertRow(0);
        newRow.innerHTML = `
            <td>${logEntry.age}</td>
            <td>${logEntry.health.toFixed(2)}</td>
            <td>${logEntry.food.toFixed(2)}</td>
            <td>${logEntry.net_health_change.toFixed(2)}</td>
            <td>${logEntry.net_food_change.toFixed(2)}</td>
            <td>${logEntry.hunting_hours}</td>
            <td>${logEntry.resting_hours}</td>
        `;
    });
}
// Function to handle strategy submission
function submitStrategy() {
    saveChartsAsImages();
    let strategyAnswer = document.querySelector("textarea[name='strategy']").value;
    var combinedChartCanvas = document.getElementById('combined-chart');
    var activityHoursChartCanvas = document.getElementById('activity-hours-chart');
    var combinedChartImage = combinedChartCanvas.toDataURL('image/png');
    var activityHoursChartImage = activityHoursChartCanvas.toDataURL('image/png');

    let formData = new FormData();
    formData.append('strategy_answer', strategyAnswer);
    formData.append('combined_chart_image', combinedChartImage);
    formData.append('activity_hours_chart_image', activityHoursChartImage);

    // Send data to the server
    fetch('/game1/submit_strategy', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob()) // Assume PDF is returned as a blob
    .then(blob => {
        // Download the PDF
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = 'result.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('There was an error!', error);
    });
}


function saveChartsAsImages() {
  var combinedChartCanvas = document.getElementById('combined-chart');
  var activityHoursChartCanvas = document.getElementById('activity-hours-chart');

  var combinedChartImage = combinedChartCanvas.toDataURL('image/png');
  var activityHoursChartImage = activityHoursChartCanvas.toDataURL('image/png');

  // Now you can send these images to the server
}


document.getElementById("answer-form").addEventListener("submit", function(event) {
    event.preventDefault();

    // Get the student's answer
    const answer = document.querySelector("textarea[name='student-answer']").value;

    // Get the current username and final age
    const username = "{{ current_user.username }}";
    const finalAge = "{{ log[-1].age + 1 }}";

    // Create a div to hold the content for the PDF
    const content = document.createElement('div');

    // Add the username and final age
    content.innerHTML += `<h1>Good work ${username}!</h1>`;
    content.innerHTML += `<h2>Your Final Age: ${finalAge}</h2>`;

    // Add the charts
    content.appendChild(document.getElementById("combined-chart"));
    content.appendChild(document.getElementById("activity-hours-chart"));

    // Add the game log table
    content.appendChild(document.getElementById("game-log"));

    // Add the student's answer
    content.innerHTML += `<h2>Your Answer:</h2><p>${answer}</p>`;

    // Generate the PDF
    const pdf = html2pdf().from(content).outputPdf();

    // Download the PDF
    const blob = new Blob([pdf], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'result.pdf';
    a.click();
    URL.revokeObjectURL(url);
});


// You can call the submitStrategy function when the form is submitted
document.querySelector("form").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent default form submission
  submitStrategy();
});
