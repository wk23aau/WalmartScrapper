document.getElementById('scan').addEventListener('click', async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (tab) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: startScanning
        });
    }
});

document.getElementById('save').addEventListener('click', async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (tab) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: saveCollectedData
        });
    }
});

function startScanning() {
    if (typeof collectWalmartData === "function") {
        collectWalmartData();
    } else {
        alert("Product scanning script not loaded properly.");
    }
}

function saveCollectedData() {
    if (typeof saveData === "function") {
        saveData();
    } else {
        alert("No data available to save.");
    }
}
