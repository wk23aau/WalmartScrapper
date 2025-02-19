// const fs = require('fs');

// // Read JSON file
// const inputFile = './cat_treat_18_02_2025.json';  // Your input JSON file
// const outputFile = 'cat_treats_no_shipping.json';

// // Read the JSON file
// fs.readFile(inputFile, 'utf8', (err, data) => {
//     if (err) {
//         console.error("❌ Error reading file:", err);
//         return;
//     }

//     try {
//         // Parse JSON data
//         const products = JSON.parse(data);

//         // Filter products based on the given conditions
//         const filteredProducts = products.filter(product => 
//             product.shipping === "N/A" && 
//             (!product.pickup || !product.pickup.toLowerCase().includes("shipping")) && 
//             (!product.delivery || !product.delivery.toLowerCase().includes("shipping"))
//         );
//         // Extract Walmart URLs from filtered products
//         const walmartUrls = filteredProducts.map(product => `https://walmart.com/ip/${product.linkIdentifier}`);

//         // Structure the output JSON
//         const outputJson = { "walmartUrls": walmartUrls };

//         // Write to a new JSON file
//         fs.writeFileSync(outputFile, JSON.stringify(outputJson, null, 2));

//         console.log(`✅ Filtered Walmart URLs (Shipping: N/A) saved to ${outputFile}`);
//     } catch (error) {
//         console.error("❌ Error parsing JSON:", error);
//     }
// });


//no filter
const fs = require('fs');

// Read JSON file
const inputFile = './energy_tea_19_02_2025.json';  // Your input JSON file
const outputFile = 'energy_tea.json';

// Read the JSON file
fs.readFile(inputFile, 'utf8', (err, data) => {
    if (err) {
        console.error("❌ Error reading file:", err);
        return;
    }

    try {
        // Parse JSON data
        const products = JSON.parse(data);

        // Extract Walmart URLs from all products (No filtering)
        const walmartUrls = products.map(product => `https://walmart.com/ip/${product.linkIdentifier}`);

        // Structure the output JSON
        const outputJson = { "walmartUrls": walmartUrls };

        // Write to a new JSON file
        fs.writeFileSync(outputFile, JSON.stringify(outputJson, null, 2));

        console.log(`✅ Walmart URLs saved to ${outputFile}`);
    } catch (error) {
        console.error("❌ Error parsing JSON:", error);
    }
});
