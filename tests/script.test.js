/**
 * @jest-environment jsdom
 */

const {
    blockIP,
    unblockIP,
    loadBlockedIPs,
    startCapture,
    stopCapture,
    updateDuration,
    downloadCSVFile,
} = require("../static/js/app.js");

describe("NIDPS Frontend Functions", () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div id="blocked-container"></div>
            <select id="interfaceDropdown">
                <option value="eth0">eth0</option>
            </select>
            <button id="startButton" disabled>Start</button>
            <span id="start-time"></span>
            <span id="end-time"></span>
            <span id="duration"></span>
        `;

        global.interfaceDropdown = document.getElementById("interfaceDropdown");
        global.startButton = document.getElementById("startButton");
        global.fetch = jest.fn();
        global.alert = jest.fn();
        global.socket = { emit: jest.fn(), on: jest.fn() };
    });

    test("startCapture sets time and emits socket event", () => {
        interfaceDropdown.value = "eth0";
        startCapture();

        expect(document.getElementById("start-time").innerText).not.toBe("");
        expect(document.getElementById("end-time").innerText).toBe("Running...");
        expect(document.getElementById("duration").innerText).toBe("0s");
        expect(global.socket.emit).toHaveBeenCalledWith("start_capture");
    });

    test("stopCapture sets end time and emits stop_capture", () => {
        stopCapture();
        expect(document.getElementById("end-time").innerText).not.toBe("");
        expect(global.socket.emit).toHaveBeenCalledWith("stop_capture");
    });

    test("updateDuration updates duration text", () => {
        global.startTime = new Date(Date.now() - 65000); // 65 seconds ago
        updateDuration();
        expect(document.getElementById("duration").innerText).toBe("1m 5s");
    });

    test("blockIP sends correct POST request", async () => {
        fetch.mockResolvedValue({
            json: () => Promise.resolve({ success: true }),
        });

        await blockIP("192.168.1.5", "test");

        expect(fetch).toHaveBeenCalledWith(
            "http://127.0.0.1:5001/block_ip",
            expect.objectContaining({
                method: "POST",
                body: JSON.stringify({ ip: "192.168.1.5", status: "test" }),
            })
        );
    });

    test("unblockIP sends correct request and calls alert", async () => {
        fetch.mockResolvedValue({
            json: () => Promise.resolve({ success: true }),
        });

        await unblockIP("192.168.1.5");

        expect(fetch).toHaveBeenCalledWith(
            "http://127.0.0.1:5001/unblock_ip",
            expect.objectContaining({
                method: "POST",
                body: JSON.stringify({ ip: "192.168.1.5" }),
            })
        );

        expect(alert).toHaveBeenCalled();
    });

    test("loadBlockedIPs updates blocked-container", async () => {
        fetch.mockResolvedValue({
            json: () =>
                Promise.resolve({
                    blocked_ips: [
                        { ip_address: "192.168.0.1", status: "System Blocked" },
                        { ip_address: "10.0.0.2", status: "Blocked by User" },
                    ],
                }),
        });

        await loadBlockedIPs();

        const container = document.getElementById("blocked-container");
        expect(container.children.length).toBe(2);
        expect(container.innerHTML).toContain("192.168.0.1");
        expect(container.innerHTML).toContain("10.0.0.2");
    });

    test("downloadCSVFile emits socket event", () => {
        downloadCSVFile();
        expect(global.socket.emit).toHaveBeenCalledWith("download_csv_file");
    });
});
