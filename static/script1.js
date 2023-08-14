// Variables for charts
let combinedChart;
let activityHoursChart;

// Get range inputs and number inputs
var huntingHoursRange = document.getElementById("hunting-hours");
var restingHoursRange = document.getElementById("resting-hours");
var huntingHoursNumber = document.getElementById("hunting-hours-input");
var restingHoursNumber = document.getElementById("resting-hours-input");



// Update number input when range input changes
function synchronizeInputs() {
    var huntingHoursRange = document.getElementById("hunting-hours");
    var restingHoursRange = document.getElementById("resting-hours");
    var huntingHoursNumber = document.getElementById("hunting-hours-input");
    var restingHoursNumber = document.getElementById("resting-hours-input");

    if (huntingHoursRange && restingHoursRange && huntingHoursNumber && restingHoursNumber) {
        huntingHoursRange.oninput = function() {
            huntingHoursNumber.value = this.value;
            restingHoursNumber.value = 24 - this.value;
            restingHoursRange.value = 24 - this.value;
        };

        restingHoursRange.oninput = function() {
            restingHoursNumber.value = this.value;
            huntingHoursNumber.value = 24 - this.value;
            huntingHoursRange.value = 24 - this.value;
        };

        huntingHoursNumber.oninput = function() {
            huntingHoursRange.value = this.value;
            restingHoursNumber.value = 24 - this.value;
            restingHoursRange.value = 24 - this.value;
        };

        restingHoursNumber.oninput = function() {
            restingHoursRange.value = this.value;
            huntingHoursNumber.value = 24 - this.value;
            huntingHoursRange.value = 24 - this.value;
        };
    }
}

window.onload = function() {
    synchronizeInputs();

    // Get the modal
    let modal = document.getElementById("top-score-modal");

    // Get the <span> element that closes the modal
    let closeButton = document.getElementsByClassName("close-button")[0];

    if (closeButton) {
        closeButton.onclick = function() {
            modal.style.display = "none";
        }
    }

    // Fetch initial game state and populate the status
    fetch("/game1/get_game_state", {
        method: "GET",
    })
    .then(response => response.json())
    .then(data => {
        updateStatus(data);
    })
    .catch(error => {
        console.error("Error fetching initial game state:", error);
    });

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Fetch the game result data and draw the charts
    fetch("/game1/get_result_data", {
        method: "GET",
    })
    .then(response => response.json())
    .then(data => {
        drawCharts(data.log);

        // Render the log data in the table
        const gameLog = document.getElementById("game-log").getElementsByTagName('tbody')[0];
        data.log.forEach(logEntry => {
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
        // Create download links for the charts
      createDownloadLinkForCombinedChart();
      createDownloadLinkForActivityHoursChart();
      createDownloadLinkForTable();
    })
    .catch(error => {
        console.error("Error:", error);
    });
};

function updateStatus(playerStatus) {
    document.getElementById("age").textContent = playerStatus.age;
    document.getElementById("health").textContent = playerStatus.health.toFixed(2);
    document.getElementById("food").textContent = playerStatus.food.toFixed(2);
}

function drawCharts(logData, gameOver) {
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

// Function to download table data as CSV or JSON
function downloadTableData(filename, data, format) {
    let content;
    if (format === 'csv') {
        const csvRows = [];
        const headers = Object.keys(data[0]);
        csvRows.push(headers.join(','));
        for (const row of data) {
            const values = headers.map(header => row[header]);
            csvRows.push(values.join(','));
        }
        content = csvRows.join('\n');
    } else if (format === 'json') {
        content = JSON.stringify(data, null, 2);
    } else {
        console.error("Invalid format provided for downloadTableData function.");
        return;
    }

    const blob = new Blob([content], { type: `text/${format === 'csv' ? 'csv' : 'json'}` });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadChartImage(chartId) {
    const canvas = document.getElementById(chartId);
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = url;
    a.download = `${chartId}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}


function submitDecision() {
    const huntingHours = parseInt(document.getElementById("hunting-hours-input").value);
    const restingHours = parseInt(document.getElementById("resting-hours-input").value);

    if (huntingHours + restingHours === 24) {
        const formData = new FormData();
        formData.append("hunting_hours", huntingHours);
        formData.append("resting_hours", restingHours);

        fetch("/game1/submit_decision", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("output").textContent = data.result_message;

            if (data.status === "error") {
            // Handle the error response
            // You can choose to disable the submit button or redirect to another page if the game is over
            if (data.result_message.includes("Game over")) {
                    document.getElementById("submit-button").style.display = "none";
            }
            return; // Exit the function here if there was an error
        }

            if (data.status === "success") {
                updateStatus(data.player_status);
                const gameLog = document.getElementById("game-log").getElementsByTagName('tbody')[0];
                const newRow = gameLog.insertRow(0);

                const logEntry = data.player_status.log[data.player_status.log.length - 1];
                newRow.innerHTML = `
                    <td>${data.player_status.age}</td>
                    <td>${data.player_status.health.toFixed(2)}</td>
                    <td>${data.player_status.food.toFixed(2)}</td>
                    <td>${logEntry.net_health_change.toFixed(2)}</td>
                    <td>${logEntry.net_food_change.toFixed(2)}</td>
                    <td>${huntingHours}</td>
                    <td>${restingHours}</td>
                `;
                drawCharts(data.player_status.log, data.result_message.includes("Game over"));

                if (data.result_message.includes("Game over")) {
                    document.getElementById("submit-button").disabled = true;
                    document.getElementById("view-results").style.display = "block"; // Show "View Results" button
                    if (data.is_top_score) {
                        modal.style.display = "block";
                    }
                    // You can choose not to redirect to the results page when the game is over
                    // window.location.href = "/results";
                } else {
                    document.getElementById("view-results").style.display = "none"; // Hide "View Results" button
                }
            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("output").textContent = "An error occurred. Please try again.";
        });
    } else {
        document.getElementById("output").textContent = "Total hours must add up to 24. Please try again.";
    }
}


function startOver() {
    fetch("/game1/reset_game", {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("output").textContent = "";
        document.getElementById("game-log").getElementsByTagName('tbody')[0].innerHTML = "";
        document.getElementById("combined-chart").style.display = "none";
        document.getElementById("activity-hours-chart").style.display = "none";
        document.getElementById("submit-button").disabled = false;
        document.getElementById("restart-button").style.display = "none";

        // Hide the "View Results" button
        document.getElementById("view-results").style.display = "none";

        // Reset input fields to default values
        document.getElementById("hunting-hours-input").value = 0;
        document.getElementById("resting-hours-input").value = 0;

        // Reset range sliders to default values
        document.getElementById("hunting-hours").value = 0; // <--- Add this line
        document.getElementById("resting-hours").value = 0; // <--- Add this line

        // Update status to reset to age 18 and initial health/food score of 50
        updateStatus(data);

        // Redraw empty charts
        drawCharts([], false);
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("output").textContent = "An error occurred. Please try again.";
    });
}



function createDownloadLinkForCombinedChart() {
  const combinedChartCanvas = document.getElementById("combined-chart");

  // Create an anchor element to hold the download link
  const downloadLink = document.createElement("a");

  // Convert the canvas to a data URL
  const dataURL = combinedChartCanvas.toDataURL("image/png");

  // Set the download link properties
  downloadLink.href = dataURL;
  downloadLink.download = "health_food_chart.png";
  downloadLink.innerHTML = "Download Health and Food Chart";

  // Append the link to the DOM
  const container = document.getElementById("download-links");
  container.appendChild(downloadLink);
}

function createDownloadLinkForActivityHoursChart() {
  const activityHoursChartCanvas = document.getElementById("activity-hours-chart");

  // Create an anchor element to hold the download link
  const downloadLink = document.createElement("a");

  // Convert the canvas to a data URL
  const dataURL = activityHoursChartCanvas.toDataURL("image/png");

  // Set the download link properties
  downloadLink.href = dataURL;
  downloadLink.download = "activity_hours_chart.png";
  downloadLink.innerHTML = "Download Activity Hours Chart";

  // Append the link to the DOM
  const container = document.getElementById("download-links");
  container.appendChild(downloadLink);
}

function createDownloadLinkForTable() {
  // Get the table element
  const gameLogTable = document.getElementById("game-log");

  // Clone the table to avoid modifying the original table on the page
  const clonedTable = gameLogTable.cloneNode(true);

  // Add the table data as a CSV content
  let csvContent = [];
  for (const row of clonedTable.rows) {
    const rowData = [];
    for (const cell of row.cells) {
      rowData.push(cell.textContent.trim());
    }
    csvContent.push(rowData.join(","));
  }
  const csvData = csvContent.join("\n");

  // Create an anchor element to hold the download link
  const downloadLink = document.createElement("a");

  // Convert the CSV data to a Blob
  const blob = new Blob([csvData], { type: "text/csv" });

  // Set the download link properties
  downloadLink.href = URL.createObjectURL(blob);
  downloadLink.download = "game_log.csv";
  downloadLink.innerHTML = "Download Game Log Table";

  // Append the link to the DOM
  const container = document.getElementById("download-links");
  container.appendChild(downloadLink);
}

console.log("script1.js is loaded!");
