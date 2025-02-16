// Walmart Shipping Filter Extension - Data Collection with Pagination
(function collectWalmartData() {
    let collectedData = [];
    
    function scrapeData() {
        document.querySelectorAll("div[io-id]").forEach(productBlock => {
            let linkElement = productBlock.querySelector("a[link-identifier]");
            let priceElement = productBlock.querySelector("div[data-automation-id='product-price']");
            let fulfillmentElement = productBlock.querySelector("div[data-automation-id='fulfillment-badge']");
            
            let currentPriceElement = priceElement ? [...priceElement.querySelectorAll("span")].find(span => span.innerText.includes("current price")) : null;
            let pricePerOzElement = priceElement ? priceElement.querySelector("div:nth-of-type(2)") : null;
            
            let currentPrice = currentPriceElement ? currentPriceElement.innerText.trim() : "N/A";
            let pricePerOz = pricePerOzElement ? pricePerOzElement.innerText.trim() : "N/A";
            
            let pickup = "N/A";
            let delivery = "N/A";
            let shipping = "N/A";
            
            if (fulfillmentElement) {
                let pickupElement = fulfillmentElement.querySelector("div:nth-of-type(1)");
                let deliveryElement = fulfillmentElement.querySelector("div:nth-of-type(2)");
                let shippingElement = fulfillmentElement.querySelector("div:nth-of-type(3)");
                
                pickup = pickupElement ? pickupElement.innerText.trim() : "N/A";
                delivery = deliveryElement ? deliveryElement.innerText.trim() : "N/A";
                shipping = shippingElement ? shippingElement.innerText.trim() : "N/A";
            }
            
            if (linkElement) {
                let linkIdentifier = linkElement.getAttribute("link-identifier");
                
                if (linkIdentifier) {
                    collectedData.push({
                        "ioId": productBlock.getAttribute("io-id"),
                        "linkIdentifier": linkIdentifier,
                        "text": linkElement.innerText.trim(),
                        "href": linkElement.getAttribute("href"),
                        "currentPrice": currentPrice,
                        "pricePerOz": pricePerOz,
                        "pickup": pickup,
                        "delivery": delivery,
                        "shipping": shipping
                    });
                    console.log(`Collected: io-id: ${productBlock.getAttribute("io-id")}, link-identifier: ${linkIdentifier}, text: ${linkElement.innerText.trim()}, href: ${linkElement.getAttribute("href")}, current price: ${currentPrice}, price per oz: ${pricePerOz}, pickup: ${pickup}, delivery: ${delivery}, shipping: ${shipping}`);
                }
            }
        });
    }
    
    function goToNextPage() {
        let nextPageButton = document.querySelector("a[data-testid='NextPage']");
        if (nextPageButton) {
            nextPageButton.click();
            setTimeout(() => collectDataWithPagination(), 5000); // Wait for next page to load
        } else {
            saveData(); // No more pages, save data
        }
    }
    
    function saveData() {
        let urlParams = new URLSearchParams(window.location.search);
        let searchTerm = urlParams.get("q") || "unknown_search";
        let filename = `${searchTerm}_all_pages.json`;
        let dataStr = JSON.stringify(collectedData, null, 2);
        let blob = new Blob([dataStr], { type: "application/json" });
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        console.log(`Final Collected Data saved to file: ${filename}`);
    }
    
    function collectDataWithPagination() {
        scrapeData();
        goToNextPage();
    }
    
    collectDataWithPagination();
})();
