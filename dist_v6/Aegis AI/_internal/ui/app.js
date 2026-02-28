const riskLevelEl = document.getElementById('risk-level');
const riskDescEl = document.getElementById('risk-desc');
const alertListEl = document.getElementById('alert-list');
const statusBoxEl = document.getElementById('status-box');
const dismissBtn = document.getElementById('dismiss-btn');

dismissBtn.addEventListener('click', async () => {
    try {
        await fetch('/api/dismiss', { method: 'POST' });
    } catch (e) {
        console.error("Failed to dismiss alerts:", e);
    }
});

// Websocket connection
let ws;

function connect() {
    ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        updateUI(data);
    };

    ws.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 2 seconds.');
        setTimeout(function () {
            connect();
        }, 2000);
    };

    ws.onerror = function (err) {
        console.error('Socket error. Closing socket');
        ws.close();
    };
}

function updateUI(data) {
    const risk = data.risk_level;
    riskLevelEl.innerText = risk;

    riskLevelEl.className = risk;

    if (risk === "GREEN") {
        riskDescEl.innerText = "Monitoring systems are active. No threats detected.";
        statusBoxEl.style.borderColor = "#4caf50";
        statusBoxEl.style.boxShadow = "0 0 15px rgba(76, 175, 80, 0.2)";
    } else if (risk === "YELLOW") {
        riskDescEl.innerText = "Caution: Anomalies or suspicious patterns present.";
        statusBoxEl.style.borderColor = "#ffeb3b";
        statusBoxEl.style.boxShadow = "0 0 15px rgba(255, 235, 59, 0.2)";
    } else if (risk === "RED") {
        riskDescEl.innerText = "THREAT WARNING: High Probability of Malicious Activity!";
        statusBoxEl.style.borderColor = "#f44336";
        statusBoxEl.style.boxShadow = "0 0 15px rgba(244, 67, 54, 0.5)";
    }

    // Handle alerts
    const alerts = data.alerts;

    if (alerts.length > 0) {
        dismissBtn.style.display = 'block';
    } else {
        dismissBtn.style.display = 'none';
        if (alertListEl.children.length === 0 || alertListEl.children[0].innerText !== "No recent threats.") {
            alertListEl.innerHTML = '<li style="border-left-color: #4caf50;">No recent threats.</li>';
        }
    }

    // Quick diff to avoid full re-render on same alerts
    if (alerts.length > 0 && alertListEl.children.length !== alerts.length + (alertListEl.children[0]?.innerText === "No recent threats." ? -1 : 0)) {
        alertListEl.innerHTML = '';
        alerts.forEach(alert => {
            const li = document.createElement('li');
            li.innerText = alert.message;
            if (alert.risk === "RED") {
                li.style.borderLeftColor = "#f44336";
            } else if (alert.risk === "YELLOW") {
                li.style.borderLeftColor = "#ffeb3b";
            } else {
                li.style.borderLeftColor = "#4caf50";
            }
            alertListEl.appendChild(li);
        });
    }
}

async function fetchApps() {
    try {
        const response = await fetch('/api/apps');
        const data = await response.json();
        const cmdList = document.getElementById('command-list');

        data.apps.forEach(app => {
            const li = document.createElement('li');
            li.innerText = `"open ${app}"`;
            cmdList.appendChild(li);
        });
    } catch (e) {
        console.error("Failed to fetch apps", e);
    }
}

fetchApps();
connect();
