// Walmart Product Page Data Collection - Debugged with Breakpoints
(function collectProductData() {
    let collectedData = {};
    
    console.log("Starting Walmart product data collection...");
    
    // Collect main title dynamically
    let titleElement = document.querySelector("h1#main-title");
    let mainTitle = titleElement ? titleElement.innerText.trim() : "N/A";
    console.log("Main Title:", mainTitle);
    collectedData["mainTitle"] = mainTitle;
    
    // Collect brand name dynamically
    let brandElement = document.querySelector("section div div a");
    let brandName = brandElement ? brandElement.innerText.trim() : "N/A";
    console.log("Brand Name:", brandName);
    collectedData["brandName"] = brandName;
    
    // Collect Ingredients dynamically from any product
    let ingredientsSections = document.querySelectorAll("section.expand-collapse-section");
    ingredientsSections.forEach(section => {
        let header = section.querySelector(".expand-collapse-header h2");
        if (header && header.innerText.includes("Ingredients")) {
            let expandButton = section.querySelector(".expand-collapse-header button");
            if (expandButton && expandButton.getAttribute("aria-expanded") === "false") {
                console.log("Clicking Ingredients Expand Button...");
                expandButton.click();
            }
            setTimeout(() => {
                let ingredientsContainer = section.querySelector("div[data-testid='ui-collapse-panel'] p");
                let ingredientsText = ingredientsContainer ? ingredientsContainer.innerText.trim() : "N/A";
                console.log("Ingredients:", ingredientsText);
                collectedData["ingredients"] = ingredientsText;
            }, 2000);
        }
    });
    
    // Collect Key Features from "About this item" section
    let aboutSection = document.querySelector("h2.b.mv0.f5.pb2");
    if (aboutSection && aboutSection.innerText.includes("About this item")) {
        let viewMoreButton = document.querySelector("button[aria-label^='View more']");
        if (viewMoreButton && viewMoreButton.getAttribute("aria-expanded") === "false") {
            console.log("Clicking View More Button for About this item...");
            viewMoreButton.click();
        }
        setTimeout(() => {
            let keyFeaturesList = document.querySelector(".expand-collapse-content ul");
            let keyFeatures = keyFeaturesList ? Array.from(keyFeaturesList.querySelectorAll("li")).map(li => li.innerText.trim()) : [];
            console.log("Key Features:", keyFeatures);
            collectedData["keyFeatures"] = keyFeatures;
        }, 2000);
    }
    
    // Collect Product Description
    let productDetailsSection = document.querySelector("#product-description-section");
    if (productDetailsSection) {
        let expandButton = productDetailsSection.querySelector("button[aria-label='Product details']");
        let isExpanded = productDetailsSection.querySelector("i.ld.ld-ChevronUp");
        if (expandButton && !isExpanded) {
            console.log("Clicking Product Details Expand Button...");
            expandButton.click();
        }
        setTimeout(() => {
            let descriptionElement = productDetailsSection.querySelector("div[data-testid='product-description-content'] p");
            let productDescription = descriptionElement ? descriptionElement.innerText.trim() : "N/A";
            console.log("Product Description:", productDescription);
            collectedData["productDescription"] = productDescription;
        }, 2000);
    }
    
    // Collect Specifications
    let specifications = {};
    let specificationsHeader = document.querySelector("h2.w-100.ma0.lh-copy.normal.pa3.f5.undefined");
    if (specificationsHeader && specificationsHeader.innerText.includes("Specifications")) {
        let expandButton = specificationsHeader.parentElement.querySelector("button[aria-label='Specifications']");
        let isExpanded = specificationsHeader.parentElement.querySelector("i.ld.ld-ChevronUp");
        if (expandButton && !isExpanded) {
            console.log("Clicking Specifications Expand Button...");
            expandButton.click();
        }
        
        setTimeout(() => {
            let specList = document.querySelectorAll("div.nt1 div.pb2, div.nt1 div");
            specList.forEach(spec => {
                let key = spec.querySelector("h3");
                let value = spec.querySelector("div span");
                if (key && value) {
                    specifications[key.innerText.trim()] = value.innerText.trim();
                }
            });
            console.log("Specifications:", specifications);
            collectedData["specifications"] = specifications;
            
            // Save collected data to a file
            let filename = `product_data_${Date.now()}.json`;
            let dataStr = JSON.stringify(collectedData, null, 2);
            let blob = new Blob([dataStr], { type: "application/json" });
            let a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            console.log(`Collected Data saved to file: ${filename}`);
        }, 3000);
    }
})();
