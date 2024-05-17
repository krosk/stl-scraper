// scripts/main.js
var map;
var myChart;

// Function to generate the icon HTML based on the number
function generateIconHTML(number, currency, capacity) {
    return `<div>${number}${currency}<br>${capacity}</div>`;
}

function updateMarkers() {
    console.log('Updating markers');

    const selectedDate = new Date(document.getElementById('date-selector').value);
    if (isNaN(selectedDate)) {
        console.log('No date set, skipping');
        return; // Check if the input is a valid date
    }
    const selectedDateString = selectedDate.toISOString().substring(0, 10);

    const capacityFilterInput = document.getElementById('capacity-selector');
    const thresholdCapacity = parseInt(capacityFilterInput.value);

    const maxPlotInput = document.getElementById('max-plot');
    const maxPlot = parseInt(maxPlotInput.value);

    fetch('/static/data.json')
        .then(response => response.json())
        .then(data => {
            // Clear existing markers
            map.eachLayer((layer) => {
                if (layer instanceof L.Marker) layer.remove();
            });

            let highlight_plot_data = [];
            let other_plot_data = [];

            for (let key in data) {
                if (data.hasOwnProperty(key)) {
                    const item = data[key];
                    for (let date in item.price_per_date) {
                        if (item.price_per_date.hasOwnProperty(date)) {
                            // Check if the marker's date matches the selected date
                            if (date === selectedDateString) {
                                if (thresholdCapacity == item.person_capacity) {
                                    let icon = L.divIcon({
                                        html: generateIconHTML(item.price_per_date[date], item.price_currency, item.person_capacity),
                                        className: 'custom-marker',
                                        iconSize: [30, 30], // Adjust as needed
                                        iconAnchor: [15, 30], // Adjust as needed
                                    });
                                    let marker = L.marker([item.latitude, item.longitude], { icon });
                                    marker.addTo(map);
                                    marker.bindPopup(`<a target="_blank" href="${item.url}">${item.name}</a><br>${item.room_type}<br>${item.house_rules}`);
                                    highlight_plot_data.push({x: item.person_capacity, y: item.price_per_date[date]});
                                } else {
                                    other_plot_data.push({x: item.person_capacity, y: item.price_per_date[date]});
                                }
                            }
                        }
                    }
                }
            }

            myChart.data.datasets[0].data = highlight_plot_data;
            myChart.data.datasets[1].data = other_plot_data;
            myChart.options.scales.y.max = maxPlot;

            myChart.update();
        })
        .catch(error => {
            document.getElementById('error-message').textContent = `Error loading data: ${error.message}`;
        });
}

function changeDate(days) {
    let dateInput = document.getElementById('date-selector');

    const currentDate = new Date(dateInput.value);
    currentDate.setDate(currentDate.getDate() + days);
    
    // Format the date as 'YYYY-MM-DD'
    const formattedDate = currentDate.toISOString().split('T')[0];

    // Set the new date value to the input field
    dateInput.value = formattedDate;

    updateMarkers();
}

function changeCapacity(delta) {
    let numberInput = document.getElementById('capacity-selector');

    const currentValue = parseInt(numberInput.value) + delta;

    // Ensure the value is within the specified range
    if (currentValue >= numberInput.min && currentValue <= numberInput.max) {
        numberInput.value = currentValue;
    } else if (currentValue < numberInput.min) {
        numberInput.value = numberInput.min; // Reset to minimum value
    } else if (currentValue > numberInput.max) {
        numberInput.value = numberInput.max; // Reset to maximum value
    }

    updateMarkers();
}

document.addEventListener("DOMContentLoaded", function () {
    map = L.map('map').setView([48.845916516034436, 2.5516667962951844], 14);
    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Set the date selector to today's date when the page loads
    let today = new Date();
    let currentDayOfMonth = today.getDate();
    today.setDate(currentDayOfMonth + 2);
    document.getElementById('date-selector').valueAsDate = today;

    // Set default capacity
    document.getElementById('capacity-selector').value = 4;

    // Create a new Chart instance
    const _data = {
        datasets: [
            {
                label: 'Selected guest count',
                data: []
            },
            {
                label: 'Other guest count',
                data: []
            }
        ]
    };

    const ctx = document.getElementById('myChart').getContext('2d');
    const config =  {
        type: 'scatter',
        data: _data,
        options: {
            animation: false,
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
            title: {
                display: true,
                text: 'Rent distribution'
                }
            },
            scales: {
                x: {
                    min: 1,
                    max: 8
                },
                y: {
                    beginAtZero: true
                }
            }
        },
    };
    myChart = new Chart(ctx, config);

    // Initialize the map with markers based on the current date
    updateMarkers();
});

async function fetchRent(){
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install('urllib3==1.26.18');
    await micropip.install('elasticsearch==8.4.3');
    await micropip.install('geopy==2.3.0');
    await micropip.install('lxml==4.9.3');
    await micropip.install('pycountry==23.12.11');
    await micropip.install('python-dotenv==1.0.0');
    await micropip.install('requests==2.28.2');
    await micropip.install('https://www.piwheels.org/simple/docopt/docopt-0.6.2-py2.py3-none-any.whl')
    await micropip.install('stlscraper-1.0-py3-none-any.whl')
    console.log(pyodide.runPython("import requests; requests.get('http://www.baidu.com')"));
}