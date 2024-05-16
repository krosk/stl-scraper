// scripts/main.js
var map;

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

    fetch('/static/data.json')
        .then(response => response.json())
        .then(data => {
            // Clear existing markers
            map.eachLayer((layer) => {
                if (layer instanceof L.Marker) layer.remove();
            });

            for (let key in data) {
                if (data.hasOwnProperty(key)) {
                    const item = data[key];
                    for (let date in item.price_per_date) {
                        if (item.price_per_date.hasOwnProperty(date) && thresholdCapacity == item.person_capacity) {
                            // Check if the marker's date matches the selected date
                            if (date === selectedDateString) {
                                let icon = L.divIcon({
                                    html: generateIconHTML(item.price_per_date[date], item.price_currency, item.person_capacity),
                                    className: 'custom-marker',
                                    iconSize: [30, 30], // Adjust as needed
                                    iconAnchor: [15, 15], // Adjust as needed
                                });
                                let marker = L.marker([item.latitude, item.longitude], { icon });
                                marker.addTo(map);
                                marker.bindPopup(`<a href="${item.url}">${item.name}</a><br>${item.room_type}<br>${item.house_rules}`);
                            }
                        }
                    }
                }
            }
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

    // Initialize the map with markers based on the current date
    updateMarkers();
});