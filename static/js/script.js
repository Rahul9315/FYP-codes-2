var socket = io.connect("http://" + document.domain + ":" + location.port);
                
let startTime;
let durationInterval;
// Initialize Data Arrays
var timestamps = [];
var packetLengths = [];

// Disable Start Button Initially
startButton.disabled = true;

// Enable Start Button on Network Selection
interfaceDropdown.addEventListener("change", function () {
    var selectedInterface = this.value;
    if (selectedInterface) {
        startButton.disabled = false;
        socket.emit("select_interface", { interface: selectedInterface });
    }
});
/*
document.getElementById("interfaceDropdown").addEventListener("change", function() {
    var selectedInterface = this.value;
    socket.emit("select_interface", { interface: selectedInterface });
});
*/
socket.on("interface_updated", function(data) {
    document.getElementById("selectedInterface").innerText = data.interface;
});

function startCapture() {

    var selectedInterface = interfaceDropdown.value;
    if (selectedInterface == "Null") {
        alert("Please choose a Network Type before starting packet capture.");
        return;
    }
    startTime = new Date(); // Capture start time
    document.getElementById("start-time").innerText = startTime.toLocaleTimeString(); // Display start time
    document.getElementById("end-time").innerText = "Running..."; // Reset end time
    document.getElementById("duration").innerText = "0s"; // Reset duration

    // Start a live clock for duration
    durationInterval = setInterval(updateDuration, 1000);

    // Emit start event to backend (if needed)
    socket.emit("start_capture");
}

function downloadCSVFile(){
    socket.emit("download_csv_file");
}

socket.on("csv_file_ready", function() {
    var link = document.createElement("a");
    link.href = "/download_csv"; // Flask route to serve the file
    link.download = "packet_data.csv"; // Suggested filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

function stopCapture() {
    let endTime = new Date(); // Capture end time
    document.getElementById("end-time").innerText = endTime.toLocaleTimeString(); // Display end time
    
    // Stop the duration clock
    clearInterval(durationInterval);
    updateDuration(); // Final update of duration

    // Emit stop event to backend (if needed)
    socket.emit("stop_capture");
}


// Function to fetch and display blocked IPs in "blocked-container"
function loadBlockedIPs() {
    fetch("http://127.0.0.1:5001/blocked_ips")
        .then(response => response.json())
        .then(data => {
            let blockedContainer = document.getElementById("blocked-container");
            blockedContainer.innerHTML = "";

            data.blocked_ips.forEach(ipObj => {
                let blockedDiv = document.createElement("div");
                blockedDiv.className = "packet-box blocked"; // Similar styling as anomaly-container

                // Create "Unblock IP" button
                let unblockButton = document.createElement("a");
                unblockButton.innerText = "Unblock IP";
                unblockButton.href = "#";
                unblockButton.className = "block-link";
                unblockButton.onclick = function(event) {
                    event.preventDefault();
                    unblockIP(ipObj.ip_address); // Call function to unblock IP
                };

                blockedDiv.innerHTML = `<strong>Blocked IP:</strong> ${ipObj.ip_address} <strong>Status:</strong> ${ipObj.status}  .`;
                blockedDiv.appendChild(unblockButton);
                blockedContainer.prepend(blockedDiv);
            });
        });
}

function updateDuration() {
    if (startTime) {
        let now = new Date();
        let elapsedSeconds = Math.floor((now - startTime) / 1000);
        let minutes = Math.floor(elapsedSeconds / 60);
        let seconds = elapsedSeconds % 60;
        document.getElementById("duration").innerText = `${minutes}m ${seconds}s`;
    }
}

// Function to block an IP when the "Block IP" button is clicked
function blockIP(ip) {
    fetch("http://127.0.0.1:5001/block_ip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`IP ${ip} has been blocked and saved to the database.`);
            loadBlockedIPs(); // Refresh the blocked IPs list
        } else {
            alert("Error blocking IP. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
}

// Function to unblock an IP when "Unblock IP" is clicked
function unblockIP(ip) {
    fetch("http://127.0.0.1:5001/unblock_ip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`IP ${ip} has been unblocked and removed from the database.`);
            loadBlockedIPs();
        } else {
            alert("Error unblocking IP. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
}



// Create Initial Graph
Plotly.newPlot("live-graph", [{
    x: [],
    y: [],
    mode: "lines",
    name: "Packet Length",
    line: { color: "red" }
}], {
    title: "Live Packet Length Over Time",
    xaxis: { title: "Time" },
    yaxis: { title: "Packet Length (bytes)" }
});

let uniqueAnomalyIPs = new Set();

var anomalyIPCount = {};  


socket.on("new_packet", function(data) {
    var packetDiv = document.createElement("div");
    packetDiv.className = "packet-box " + (data.status === "Anomaly" ? "anomaly" : "normal");
    packetDiv.innerHTML = `<strong>Size:</strong> ${data.packet_length} | <strong>Packet:</strong> ${data.src_ip} → ${data.dst_ip} | <strong>Service:</strong> ${data.service} | <strong>Protocol:</strong> ${data.protocol} | <strong>Status:</strong> ${data.status}`;
    document.getElementById("packet-container").prepend(packetDiv);

    // Update system IP and packet count
    document.getElementById("system-ip").innerText = data.system_ip;
    document.getElementById("packet-count").innerText = data.packet_count;

    // If the packet is Anomaly, also display it in Anomaly section
    if (data.status === "Anomaly") {
        var anomalyDiv = document.createElement("div");
        anomalyDiv.className = "packet-box anomaly";
        
        // Object to store counts of packets for each anomaly IP                          

        if (data.src_ip !== data.system_ip ){//&& data.src_ip !== '192.168.1.254') {
            // Check if the IP already exists in our tracking object
            if (anomalyIPCount[data.src_ip]) {
                anomalyIPCount[data.src_ip] += 1; // Increment count

                // Update the packet count in the UI
                var packetCountElement = document.getElementById(`count-${data.src_ip}`);
                if (packetCountElement) {
                    packetCountElement.innerText = anomalyIPCount[data.src_ip];
                }
            } else {
                // First occurrence of this IP, initialize count
                anomalyIPCount[data.src_ip] = 1;

                // Create a new div for the anomaly IP
                var anomalyDiv = document.createElement("div");
                anomalyDiv.className = "packet-box anomaly";
                anomalyDiv.id = `anomaly-${data.src_ip}`; // Unique ID for the div

                // Create an anchor element (styled as a button)
                var blockLink = document.createElement("a");
                blockLink.innerText = "Block IP";
                blockLink.href = "#";  // Prevents page reload
                blockLink.className = "block-link"; // Apply CSS styling

                // On click, prevent default link behavior and call the function
                blockLink.onclick = function(event) {
                    event.preventDefault();  // Prevents the anchor from navigating
                    blockIP(data.src_ip);  // Call function to save the IP
                };

                // Set inner HTML with a unique span for count updates
                anomalyDiv.innerHTML = `<strong>IP:</strong> ${data.src_ip} 
                                        <strong>( ${data.protocol} ) </strong>
                                        <strong>Packets:</strong> <span id="count-${data.src_ip}">1</span>    `;

                // Append the button
                anomalyDiv.appendChild(blockLink);

                // Prepend the new div to the container
                document.getElementById("anomaly-container").prepend(anomalyDiv);
            }
        }

        if (timestamps.length > 50) {
            timestamps.shift();
            packetLengths.shift();
        }

        // Update Graph it captures Anomaly only
        Plotly.update("live-graph", { x: [timestamps], y: [packetLengths] });

            
    }

    timestamps.push(new Date(data.timestamp * 1000));  // Convert timestamp
    packetLengths.push(data.packet_length);

    Plotly.react("pie-chart", [{
        values: [data.count_Normal_Anomaly.normal, data.count_Normal_Anomaly.anomaly],
        labels: ["Normal", "Anomaly"],
        type: "pie",
        marker: { colors: ["#28a745", "#dc3545"] }
    }]);

    

});

window.onload = loadBlockedIPs;