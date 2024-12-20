let waterStatus = "off";  
let shadeStatus = "off";
let waterTimer = null;
function toggleWater() {
    // Clear any existing timer when manually toggling water
    clearTimeout(waterTimer);

    // Toggle water status
    waterStatus = (waterStatus === "off") ? "on" : "off"; 
    
    // Update the button text or color based on the status
    const waterButton = document.getElementById("Water");
    const waterStatusText = document.getElementById("Water-text");

    if (waterStatus === "on") {
        waterButton.style.backgroundColor = "green";  
        waterStatusText.innerText = "Water is on";    

        // Start the timer if a duration is selected
        const timerDuration = parseInt(document.getElementById("timer-select").value, 10);
        if (timerDuration > 0) {
            waterTimer = setTimeout(() => {
                waterStatus = "off";
                waterButton.style.backgroundColor = "red";  
                waterStatusText.innerText = "Water is off";
                console.log("Water timer ended, turning off water");

               
                fetch('/api/toggle-water', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ waterStatus: waterStatus, waterInterval: timerDuration })
                });
            }, timerDuration * 60 * 1000); // min to milliseconds
            console.log(`Water will turn off in ${timerDuration} minute(s)`);
        }
    } else {
        waterButton.style.backgroundColor = "red";    
        waterStatusText.innerText = "Water is off";   
    }

    
    fetch('/api/toggle-water', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waterStatus: waterStatus })
    })
    .then(response => response.json())
    .then(data => console.log("Water status updated:", data))
    .catch(error => console.error('Error:', error));
}

function toggleShade() {

shadeStatus = (shadeStatus === "off") ? "on" : "off";

const shadeButton = document.getElementById("Shade");
const shadeStatusText= document.getElementById("Shade-text");

if (shadeStatus === "on") {

    shadeButton.style.backgroundColor = "green";
    shadeStatusText.innerText = "Shade is on";
}
else {


    shadeButton.style.backgroundColor = "red";
    shadeStatusText.innerText = "Shade is off";

}

fetch('/api/toggle-shade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ shadeStatus: shadeStatus })
})
.then(response => response.json())
.then(data => console.log("Shade status updated:", data))
.catch(error => console.error('Error:', error));


}


// Threshold

let moistureThreshold = 50;

function updateThreshold() {
   
    const inputElement = document.getElementById("moisture-threshold");
    const newThreshold = parseInt(inputElement.value, 10);

    // 0 - 100
    if (isNaN(newThreshold) || newThreshold < 0 || newThreshold > 100) {
        alert("Please enter a valid number between 0 and 100.");
        window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
        return;
        
    }

    
    moistureThreshold = newThreshold;

    
    document.getElementById("threshold-display").innerText = `Current Threshold: ${moistureThreshold}%`;

    
    fetch('/api/set-threshold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold: moistureThreshold })
    })
    .then(response => response.json())
    .then(data => console.log("Threshold updated:", data))
    .catch(error => console.error('Error:', error));
}

let moistureValue = 69;

function updateHumidity() {
    fetch('/api/get-moisture')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            
            moistureValue = data.moisture;
            document.getElementById("Humidity-text").innerText = `Current Moisture Levels: ${moistureValue}%`;
        })
        .catch(error => {
            console.error('Error fetching moisture data:', error);
            document.getElementById("Humidity-text").innerText = "Error fetching moisture data";
        });
}

// Update every 2 seconds
setInterval(updateHumidity, 2000);


// Menu for moisture
document.addEventListener("keydown", function (event) {
    if (event.key === "m" || event.key === "M") {
        const modal = document.getElementById("moisture-chart-modal");
        modal.style.display = "flex";
    }
});

document.getElementById("close-modal").addEventListener("click", function () {
    const modal = document.getElementById("moisture-chart-modal");
    modal.style.display = "none";
});


window.addEventListener("click", function (event) {
    const modal = document.getElementById("moisture-chart-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
});