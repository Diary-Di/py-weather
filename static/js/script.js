function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showWeather, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showWeather(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    fetch('/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon })
    })
    .then(response => response.json())
    .then(data => {
        const div = document.getElementById('weatherResult');

        if (data.error) {
            div.innerHTML = `<div class="alert alert-danger text-center">${data.error}</div>`;
        } else {
            let forecastHTML = '';

            if (data.forecast && data.forecast.length > 0) {
                forecastHTML = `
                    <h4 class="mb-3 text-center">3-Day Forecast</h4>
                    <div class="row text-center fw-semibold text-secondary">

                        <!-- 🌡️ Temperature -->
                        <div class="col">
                            
                            <div class="mb-1 d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 40px;">${day.weekday}</div>`).join('')}
                            </div>
                            <div class="d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 60px;">${day.temp}</div>`).join('')}
                            </div>
                        </div>

                        <!-- 💧 Humidity -->
                        <div class="col">
                            
                            <div class="mb-1 d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 40px;">${day.weekday}</div>`).join('')}
                            </div>
                            <div class="d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 40px;">${day.humidity}%</div>`).join('')}
                            </div>
                        </div>

                        <!-- 💨 Wind -->
                        <div class="col">
                            
                            <div class="mb-1 d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 40px;">${day.weekday}</div>`).join('')}
                            </div>
                            <div class="d-flex justify-content-center gap-3">
                                ${data.forecast.map(day => `<div style="min-width: 50px;">${day.wind} m/s</div>`).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }

            div.innerHTML = `
                <div class="card p-4 text-center">
                    <h2 class="mb-4">${data.city}</h2>

                    <div class="row mb-4">
                        <div class="col">
                            <h5>🌡️ Temperature</h5>
                            <p class="fw-bold mb-0" style="font-size: 1.5rem;">${data.temperature_current}°</p>
                            <p class="text-muted">${data.temperature}</p>
                        </div>
                        <div class="col">
                            <h5>💧 Humidity</h5>
                            <p class="fw-bold">${data.humidity}%</p>
                        </div>
                        <div class="col">
                            <h5>💨 Wind</h5>
                            <p class="fw-bold">${data.wind} m/s</p>
                        </div>
                    </div>

                    ${forecastHTML}
                </div>
            `;
        }
    });
}

function showError(error) {
    alert("Unable to get your location.");
}
