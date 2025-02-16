// Walmart Product Page Data Collection - Title, Brand, Ingredients, Key Features & Product Details
(function collectProductData() {
    let collectedData = {};
    
    // Collect main title dynamically
    let titleElement = document.querySelector("h1#main-title");
    let mainTitle = titleElement ? titleElement.innerText.trim() : "N/A";
    collectedData["mainTitle"] = mainTitle;
    
    // Collect brand name dynamically
    let brandElement = document.querySelector("section div div a");
    let brandName = brandElement ? brandElement.innerText.trim() : "N/A";
    collectedData["brandName"] = brandName;
    
    // Collect Ingredients dynamically from any product
    let ingredientsText = "N/A";
    let ingredientsSections = document.querySelectorAll("section.expand-collapse-section");
    ingredientsSections.forEach(section => {
        let header = section.querySelector(".expand-collapse-header h2");
        if (header && header.innerText.includes("Ingredients")) {
            let expandButton = section.querySelector(".expand-collapse-header button");
            if (expandButton && expandButton.getAttribute("aria-expanded") === "false") {
                expandButton.click(); // Click to expand
            }
            setTimeout(() => {
                let ingredientsContainer = section.querySelector("div[data-testid='ui-collapse-panel'] p");
                if (ingredientsContainer) {
                    collectedData["ingredients"] = ingredientsContainer.innerText.trim();
                }
            }, 2000); // Wait for expansion before retrieving data
        }
    });
    
    // Collect Key Features from "About this item" section
    let keyFeatures = [];
    let aboutSection = document.querySelector("h2.b.mv0.f5.pb2");
    if (aboutSection && aboutSection.innerText.includes("About this item")) {
        let viewMoreButton = document.querySelector("button[aria-label^='View more']");
        if (viewMoreButton && viewMoreButton.getAttribute("aria-expanded") === "false") {
            viewMoreButton.click(); // Click to expand
            setTimeout(() => {
                let keyFeaturesList = document.querySelector(".expand-collapse-content ul");
                if (keyFeaturesList) {
                    keyFeatures = Array.from(keyFeaturesList.querySelectorAll("li")).map(li => li.innerText.trim());
                }
                collectedData["keyFeatures"] = keyFeatures;
            }, 2000); // Wait for expansion before retrieving data
        } else {
            let keyFeaturesList = document.querySelector(".expand-collapse-content ul");
            if (keyFeaturesList) {
                keyFeatures = Array.from(keyFeaturesList.querySelectorAll("li")).map(li => li.innerText.trim());
            }
            collectedData["keyFeatures"] = keyFeatures;
        }
    }
    
    // Collect Product Description
    let productDescription = "N/A";
    let productDetailsSection = document.querySelector("#product-description-section");
    if (productDetailsSection) {
        let expandButton = productDetailsSection.querySelector("button[aria-label='Product details']");
        let isExpanded = productDetailsSection.querySelector("i.ld.ld-ChevronUp");
        if (expandButton && !isExpanded) {
            expandButton.click();
        }
        setTimeout(() => {
            let descriptionElement = productDetailsSection.querySelector("div[data-testid='product-description-content'] p");
            if (descriptionElement) {
                productDescription = descriptionElement.innerText.trim();
            }
            collectedData["productDescription"] = productDescription;
            
            // Save collected data to a file
            let filename = `product_data.json`;
            let dataStr = JSON.stringify(collectedData, null, 2);
            let blob = new Blob([dataStr], { type: "application/json" });
            let a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            console.log(`Collected Data saved to file: ${filename}`);
        }, 2000);
    }
})();
