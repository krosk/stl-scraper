// scripts/main.js
var map;
var myChart;
var pyodide;

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

    let data = JSON.parse(localStorage.getItem('data')) || {};

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

function changeRentMaxPlot(delta) {
    const maxPlotInput = document.getElementById('max-plot');
    const maxPlot = parseInt(maxPlotInput.value);

    maxPlotInput.value = maxPlot + delta;

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
    M.AutoInit();
    
    const mapCenterLat = localStorage.getItem('map_center_lat') || 48.845916516034436;
    const mapCenterLng = localStorage.getItem('map_center_lng') || 2.5516667962951844;

    // initialize map
    map = L.map('map').setView([mapCenterLat, mapCenterLng], 17);
    
    map.addEventListener('mousemove', function(ev) {
        localStorage.setItem('map_center_lat', map.getCenter().lat);
        localStorage.setItem('map_center_lng', map.getCenter().lng);
    });

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // dates elector
    let today = new Date();
    let currentDayOfMonth = today.getDate();
    today.setDate(currentDayOfMonth + 2);

    var elems = document.querySelectorAll('.datepicker');
    var instances = M.Datepicker.init(elems, {
        format: 'yyyy-mm-dd',
        defaultDate: today,
        setDefaultDate: true,
        onSelect: updateMarkers
    });

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

    const maxPlotInput = document.getElementById('max-plot');
    maxPlotInput.value = 100; // default value

    const ctx = document.getElementById('myChart').getContext('2d');
    const config =  {
        type: 'scatter',
        data: _data,
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
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
                    title: {
                        display: true,
                        text: 'Guests'
                    },
                    min: 1,
                    max: 8
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Rent (EUR)'
                    },
                }
            }
        },
    };
    myChart = new Chart(ctx, config);

    initializePython();

    updateMarkers();
});

function showMain() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('main').style.display = 'block';

    // map must be force-refreshed
    map.invalidateSize();
}

function hideMain() {
    document.getElementById('main').style.display = 'none';
    document.getElementById('loader').style.display = 'flex';
}

function resetData(){
    localStorage.setItem("data", "{}");

    updateMarkers();
}

async function callPython(script, context) {
    try {
        const { results, error } = await asyncRun(script, context);
        if (results) {
            //console.log("pyodideWorker return results: ", results);
            return results;
        } else if (error) {
            console.log("pyodideWorker error: ", error);
        }
    } catch (e) {
        console.log(
            `Error in pyodideWorker at ${e.filename}, Line: ${e.lineno}, ${e.message}`,
        );
    }
}

async function initializePython(){
    await callPython();

    // initializePython is async, so displaying the main div must happen next
    showMain();
}

async function fetchRent(){
    // disable button
    let fetchButton = document.getElementById('fetch-button');
    fetchButton.classList.add('disabled');
    let fetchSpinner = document.getElementById('busy-fetch-spinner');
    fetchSpinner.style.display = "block";

    let data = localStorage.getItem('data') || "{}";

    let dateInput = document.getElementById('date-selector');
    const checkinDate = new Date(dateInput.value);
    const checkoutDate = new Date(dateInput.value);
    checkoutDate.setDate(checkoutDate.getDate() + 2);
    const formattedCheckinDate = checkinDate.toISOString().split('T')[0];
    const formattedCheckoutDate = checkoutDate.toISOString().split('T')[0];

    const bounds = map.getBounds();
    const northEast = bounds.getNorthEast();
    const southWest = bounds.getSouthWest();
    const neLat = northEast.lat;
    const neLng = northEast.lng;
    const swLat = southWest.lat;
    const swLng = southWest.lng;

    let query = `stl.main.main(['search', "*", "--currency=EUR", "--checkin=${formattedCheckinDate}", "--checkout=${formattedCheckoutDate}", "--interval=2", "--search_by_map=true", "--ne_lat=${neLat}", "--ne_lng=${neLng}", "--sw_lat=${swLat}", "--sw_lng=${swLng}", "--storage=json", "--projectpath=/", '-v'])`;
    console.log(query)

    const file = await callPython(query, {data: data});
    localStorage.setItem("data", file);

    fetchButton.classList.remove('disabled');
    fetchSpinner.style.display = "none";

    updateMarkers();
}