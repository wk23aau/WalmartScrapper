chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "saveData") {
        chrome.scripting.executeScript({
            target: { allFrames: true },
            func: saveData
        });
    }
});

function saveData() {
    let data = localStorage.getItem("collectedData");
    if (!data) {
        alert("No data to save.");
        return;
    }
    let blob = new Blob([data], { type: "application/json" });
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = "scanned_products.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
