import gspread
import pandas as pd
import re
import json
import tkinter as tk
from tkinter import filedialog
from google.oauth2.service_account import Credentials
import random

# --- Constants ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "15QxK3A3uYjZNveb7qWFIZsuKJ7K1W9OozFksXdlapIg"
CREDENTIALS_FILE = "./credentials.json"
IMAGE_COLUMN_COUNT = 5  # Consistent image limit
DEFAULT_SELLING_PRICE = 9.99
LIGHT_ORANGE_HEX = "#FFE0B2"  # Light orange background for default price
LIGHT_GREEN_HEX = "#C8E6C9"   # Light green background for user-edited price
DEFAULT_REFERRAL_FEE = 9.99 # Default Referral Fee Value - Updated to 9.99 as per user request
DEFAULT_LABEL_FEE = 4.5  # Default Label Fee
DEFAULT_PROCESSING_FEE = 0.5 # Default Processing Fee


# --- Category and Referral Fee Data ---
CATEGORY_REFERRAL_FEES = {
    "Apparel & Accessories": {"default": 0.15, "tiers": {15: 0.05, 20: 0.10}, "keywords": ["clothing", "apparel", "fashion", "accessories", "wear", "garment", "outfit", "jewelry", "handbags", "sunglasses", "shoes"]},
    "Automotive & Powersports": {"default": 0.12, "keywords": ["automotive", "powersports", "car", "truck", "motorcycle", "vehicle", "auto parts"]},
    "Automotive Electronics": {"default": 0.08, "keywords": ["automotive electronics", "car audio", "car video", "gps", "auto security"]},
    "Baby": {"default": 0.15, "tiers": {10: 0.08}, "keywords": ["baby", "infant", "toddler", "nursery", "baby gear", "diapering", "baby food"]},
    "Beauty": {"default": 0.15, "tiers": {10: 0.08}, "keywords": ["beauty", "makeup", "skincare", "hair care", "fragrance", "cosmetics", "personal care"]},
    "Books": {"default": 0.15, "keywords": ["books", "reading", "literature", "fiction", "non-fiction", "textbooks", "novels"]},
    "Camera & Photo": {"default": 0.08, "keywords": ["camera", "photo", "photography", "digital camera", "camcorder", "lens", "tripod"]},
    "Cell Phones": {"default": 0.08, "keywords": ["cell phones", "smartphones", "mobile phones", "cellphone accessories"]},
    "Consumer Electronics": {"default": 0.08, "keywords": ["consumer electronics", "electronics", "tv", "television", "audio", "video", "home theater", "gadgets"]},
    "Compact Appliances": {"default": 0.08, "tiers": {300: 0.12}, "keywords": ["compact appliances", "small appliances", "microwave", "toaster oven", "blender", "coffee maker"]},
    "Electronics Accessories": {"default": 0.08, "tiers": {100: 0.15}, "keywords": ["electronics accessories", "computer accessories", "phone accessories", "cables", "adapters", "chargers"]},
    "Decor": {"default": 0.15, "keywords": ["decor", "home decor", "decorative", "ornaments", "vases", "candles", "wall decor"]},
    "Gourmet Food": {"default": 0.15, "keywords": ["gourmet food", "specialty food", "fine food", "luxury food", "premium food", "delicacies"]},
    "Grocery & Beverages": {"default": 0.08, "tiers": {15: 0.15}, "keywords": ["grocery", "beverages", "drinks", "food", "pantry", "snacks", "beverage", "tea", "coffee", "juice", "soda", "water", "mix", "iced tea", "powdered drink", "cereal", "pasta", "canned goods", "baking supplies"]},
    "Health & Personal Care": {"default": 0.15, "tiers": {10: 0.08}, "keywords": ["health", "personal care", "wellness", "vitamins", "supplements", "medical supplies", "first aid", "oral care", "skin care", "hair care"]},
    "Home & Garden": {"default": 0.15, "keywords": ["home", "garden", "furniture", "home improvement", "lawn & garden", "patio", "outdoor living", "home décor"]},
    "Indoor & Outdoor Furniture": {"default": 0.10, "tiers": {200: 0.15}, "keywords": ["furniture", "indoor furniture", "outdoor furniture", "living room furniture", "bedroom furniture", "dining room furniture", "patio furniture"]},
    "Industrial & Scientific": {"default": 0.12, "keywords": ["industrial", "scientific", "lab supplies", "safety equipment", "manufacturing", "construction"]},
    "Jewelry": {"default": 0.05, "tiers": {250: 0.20}, "keywords": ["jewelry", "necklaces", "earrings", "rings", "bracelets", "watches", "fine jewelry", "fashion jewelry"]},
    "Kitchen": {"default": 0.15, "keywords": ["kitchen", "cooking", "dining", "kitchen appliances", "cookware", "bakeware", "kitchen tools", "tableware"]},
    "Luggage & Travel Accessories": {"default": 0.15, "keywords": ["luggage", "travel accessories", "suitcases", "backpacks", "travel bags", "luggage sets", "passport holders"]},
    "Major Appliances": {"default": 0.08, "keywords": ["major appliances", "refrigerators", "washers", "dryers", "ovens", "dishwashers"]},
    "Music": {"default": 0.15, "keywords": ["music", "cds", "vinyl", "records", "musical instruments", "audio recordings"]},
    "Musical Instruments": {"default": 0.12, "keywords": ["musical instruments", "guitars", "keyboards", "drums", "pianos", "violins", "band instruments", "orchestral instruments"]},
    "Office Products": {"default": 0.15, "exceptions": {"Calculators": 0.08, "Printer Cartridges": 0.12}, "keywords": ["office products", "office supplies", "stationery", "paper", "ink", "toner", "printer", "calculator"]},
    "Outdoor Power Tools": {"default": 0.08, "tiers": {500: 0.15}, "keywords": ["outdoor power tools", "lawnmowers", "leaf blowers", "chainsaws", "generators", "pressure washers"]},
    "Outdoors": {"default": 0.15, "exceptions": {"Hunting Trail Monitors": 0.08, "Binoculars": 0.08, "Telescopes": 0.08, "Spotting Scopes": 0.08, "Night Vision Goggles": 0.08}, "keywords": ["outdoors", "outdoor recreation", "camping", "hiking", "fishing", "hunting", "sports", "binoculars", "telescopes", "spotting scopes", "night vision"]},
    "Personal Computers": {"default": 0.06, "keywords": ["personal computers", "desktops", "laptops", "notebooks", "pcs", "computer systems"]},
    "Pet Supplies": {"default": 0.15, "keywords": ["pet supplies", "pet food", "pet accessories", "dog food", "cat food", "pet toys", "pet care"]},
    "Plumbing, Heating, Cooling & Ventilation": {"default": 0.10, "keywords": ["plumbing", "heating", "cooling", "ventilation", "hvac", "pipes", "faucets", "water heaters", "air conditioners", "furnaces"]},
    "Shoes, Handbags & Sunglasses": {"default": 0.15, "keywords": ["shoes", "handbags", "sunglasses", "footwear", "fashion accessories", "eyewear", "wallets", "purses"]},
    "Software & Computer Video Games": {"default": 0.15, "keywords": ["software", "computer games", "video games", "pc games", "gaming software", "operating systems", "applications"]},
    "Sporting Goods": {"default": 0.15, "keywords": ["sporting goods", "sports equipment", "fitness", "exercise", "team sports", "outdoor gear", "athletic wear"]},
    "Tires & Wheels": {"default": 0.10, "keywords": ["tires", "wheels", "automotive tires", "car tires", "truck tires", "wheel accessories"]},
    "Tools & Home Improvement": {"default": 0.15, "exceptions": {"Base Power Tools": 0.12}, "keywords": ["tools", "home improvement", "hardware", "power tools", "hand tools", "building materials", "electrical", "lighting"]},
    "Toys & Games": {"default": 0.15, "keywords": ["toys", "games", "children's toys", "board games", "video games", "puzzles", "dolls", "action figures", "educational toys"]},
    "Video & DVD": {"default": 0.15, "keywords": ["video", "dvd", "movies", "films", "tv shows", "blu-ray", "video recordings"]},
    "Video Game Consoles": {"default": 0.08, "keywords": ["video game consoles", "gaming consoles", "playstation", "xbox", "nintendo", "game systems"]},
    "Video Games": {"default": 0.15, "keywords": ["video games", "gaming", "console games", "pc games", "electronic games"]},
    "Watches": {"default": 0.03, "tiers": {1500: 0.15}, "keywords": ["watches", "timepieces", "wrist watches", "luxury watches", "fashion watches", "smartwatches"]},
    "Everything Else": {"default": 0.15, "keywords": ["other", "miscellaneous", "various", "uncategorized", "general merchandise", "everything else"]} # Added keywords for "Everything Else" for clarity
}


# --- Helper Functions ---
def extract_images(images_json):
    """Extracts up to IMAGE_COLUMN_COUNT image URLs from a JSON string or a single URL string."""
    image_urls = []
    try:
        images_data = json.loads(images_json)
        if isinstance(images_data, list):
            for img in images_data:
                if isinstance(img, dict) and "images-src" in img:
                    clean_url = img["images-src"].split("?")[0]
                    image_urls.append(clean_url)
                    if len(image_urls) == IMAGE_COLUMN_COUNT:
                        break
        elif isinstance(images_data, str):
            image_urls.append(images_data.split("?")[0])
    except json.JSONDecodeError:
        print(f"Warning: JSONDecodeError for images data: {images_json[:50]}...") # Improved error handling
        pass # Or consider a more robust error handling like logging

    # Pad to ensure consistent number of image URLs, if fewer were extracted
    while len(image_urls) < IMAGE_COLUMN_COUNT:
        image_urls.append("")
    return image_urls[:IMAGE_COLUMN_COUNT] # Enforce limit consistently

def extract_summary(heading, summary):
    """Ensures summary is properly formatted, using heading as fallback if too short."""
    summary = str(summary).strip()
    return summary if len(summary) >= 40 else heading

def extract_key_features(keyfeatures_raw, summary):
    """
    Extracts key features from JSON. If too short, uses sentences from summary.
    Returns: key_feature_1, key_feature_2, remaining_key_features
    """
    key_feature_1, key_feature_2, remaining_key_features = "", "", "" # Initialize
    try:
        keyfeatures_list = json.loads(keyfeatures_raw)
        if isinstance(keyfeatures_list, list):
            keyfeatures = [kf.get("keyfeatures", "") for kf in keyfeatures_list if "keyfeatures" in kf]
        else:
            keyfeatures = []
    except json.JSONDecodeError:
        keyfeatures = []

    if len(" ".join(keyfeatures)) < 40:
        if isinstance(summary, str): # Check if summary is a string before splitting
            keyfeatures = summary.split(". ")
        else:
            keyfeatures = [] # Handle case where summary is not a string

    if keyfeatures: # Check if keyfeatures is not empty before indexing
        key_feature_1 = keyfeatures[0] if len(keyfeatures) > 0 else ""
        key_feature_2 = keyfeatures[1] if len(keyfeatures) > 1 else ""
        remaining_key_features = ". ".join(keyfeatures[2:]) if len(keyfeatures) > 2 else ""

    return key_feature_1, key_feature_2, remaining_key_features

def extract_categories(breadcrumb_json):
    """
    Extracts up to 4 category levels and their URLs from schema_org_breadcrumbs JSON.
    Returns two lists: category names and category URLs.
    """
    category_names = ["", "", "", ""]  # Default empty category names
    category_urls = ["", "", "", ""]   # Default empty category URLs
    try:
        breadcrumb_data = json.loads(breadcrumb_json)
        if "itemListElement" in breadcrumb_data:
            for item in breadcrumb_data["itemListElement"]:
                position = item.get("position", 0)
                if 1 <= position <= 4:
                    category_names[position - 1] = item.get("item", {}).get("name", "")
                    category_urls[position - 1] = item.get("item", {}).get("@id", "") # Extract URL
    except json.JSONDecodeError:
        pass

    return category_names, category_urls

def get_product_category(category_names, category_urls, heading, summary):
    """
    Determines the product category by matching keywords in category names, URLs, heading, and summary.
    Prioritizes category names and URLs, then falls back to heading and summary.
    """
    category_text = category_names + category_urls  # Prioritize category breadcrumbs
    product_text = [heading, summary]

    for category_source_list in [category_text, product_text]: # Prioritize category text
        combined_text = " ".join(category_source_list).lower()
        for category, fee_data in CATEGORY_REFERRAL_FEES.items():
            keywords = fee_data.get("keywords", [])
            if any(keyword in combined_text for keyword in keywords):
                return category  # Return category match from prioritized text

    return "Everything Else" # Default if no match in prioritized texts


def calculate_referral_fee(category, price):
    """
    Calculates the referral fee percentage based on the product category and price.
    """
    fee_data = CATEGORY_REFERRAL_FEES.get(category, CATEGORY_REFERRAL_FEES["Everything Else"])
    default_rate = fee_data.get("default", 0.15)
    tiers = fee_data.get("tiers", {})
    exceptions = fee_data.get("exceptions", {})

    if exceptions: # Exception handling (example for Office Products and Outdoors)
        if category == "Office Products" and ("calculator" in category.lower() or "calculator" in category.lower()): #Example keyword check
            return exceptions.get("Calculators", default_rate)
        if category == "Office Products" and ("printer" in category.lower() or "printer" in category.lower()) and ("cartridge" in category.lower() or "cartridges" in category.lower()): #Example keyword check
            return exceptions.get("Printer Cartridges", default_rate)
        if category == "Outdoors" and any(keyword.lower() in category.lower() or keyword.lower() in category.lower() for keyword in exceptions): # Keyword list check
            for keyword in exceptions:
                if keyword.lower() in category.lower() or keyword.lower() in category.lower():
                    return exceptions.get(keyword, default_rate)


    if price is not None:
        for threshold in sorted(tiers.keys()): #Iterate through price tiers
            if price <= threshold:
                return tiers[threshold]
    return default_rate

def extract_details_keyword_grouped(details_text):
    """
    Extracts values from a text string based on the keyword '{"details":"'.
    Takes the text after '{"details":"' until the next '}'.
    Groups the extracted values into pairs.

    Args:
        details_text (str): The input text string.

    Returns:
        dict: A dictionary with "AD values" key containing a list of lists,
              where each inner list is a pair of extracted values.
    """

    extracted_values = []
    start_index = 0
    while True:
        start_keyword_index = details_text.find('{"details":"', start_index)
        if start_keyword_index == -1:
            break  # No more keywords found

        value_start_index = start_keyword_index + len('{"details":"')
        value_end_index = details_text.find('"}', value_start_index)

        if value_end_index != -1:
            value = details_text[value_start_index:value_end_index]
            extracted_values.append(value)
            start_index = value_end_index + len('"}') # Move start_index past the closing "}"
        else:
            break  # Malformed data, no closing '}' found

    output_dict = {"AD values": []} # Changed key name to "AD values"
    value_pairs = []
    for index, value in enumerate(extracted_values):
        value_pairs.append(value)
        if (index + 1) % 2 == 0: # Form pairs every two values
            output_dict["AD values"].append(value_pairs)
            value_pairs = [] # Reset for the next pair
    if value_pairs: # Handle odd number of values if any remain
        output_dict["AD values"].append(value_pairs) # Append the last incomplete pair

    return output_dict

def extract_details_excel_keyword_grouped(excel_file):
    """
    Extracts details from an XLSX file, processing the 'details' column
    using the keyword-based extraction and grouping logic.
    Skips rows where 'details' column is empty or not a string.

    Args:
        excel_file (str): Path to the XLSX file.

    Returns:
        dict: A dictionary where keys are row indices and values are dictionaries
              containing the grouped extracted values under the "AD values" key.
              Only includes rows with valid 'details' content.
    """

    df = pd.read_excel(excel_file)
    extracted_data_dict = {}

    for index, row in df.iterrows():
        details_text = row['details']
        if not isinstance(details_text, str) or not details_text: # Check if details_text is valid and not empty
            continue # Skip to the next row if details_text is not a valid string or is empty

        row_output = extract_details_keyword_grouped(details_text)
        extracted_data_dict[index] = row_output

    return extracted_data_dict


def load_excel(file_path):
    """Load and preprocess Excel file."""
    df = pd.read_excel(file_path, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    return df

def extract_product_id(url):
    """Extract product ID from web-scraper-start-url."""
    match = re.search(r'/ip/(\d+)', url)
    return str(match.group(1)) if url and match else "" # More robust extraction

def extract_numeric_price(market_price):
    """Extracts only the numeric part of the price and converts it to float."""
    price_match = re.findall(r'\d+\.\d+|\d+', str(market_price))
    return float(price_match[0]) if price_match else None

def get_random_brand():
    """Returns a random brand name from a predefined list."""
    brands = [
        "Nexora", "Bravora", "Veltrix", "Zenovia", "Stratosync", "Lumosia",
        "Aetheron", "Novatrax", "Veridyn", "Omnexis", "Quentis", "Evolvex",
        "Zyphoria", "Synergex", "Vortexis", "Aquilora", "Fluxora", "Hypernova",
        "Cognitron", "Elevonix"
    ]
    return random.choice(brands)

def authenticate_gspread(creds_path=CREDENTIALS_FILE):
    """Authenticate and return the Google Sheets client."""
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)

def get_worksheet(client, sheet_id=SPREADSHEET_ID, sheet_index=0):
    """Return the worksheet object."""
    sheet = client.open_by_key(sheet_id)
    return sheet.get_worksheet(sheet_index)

def get_existing_product_ids(worksheet):
    """Fetch existing product IDs and their row indices."""
    existing_data = worksheet.get_all_values()
    return {row[1].strip(): idx + 1 for idx, row in enumerate(existing_data) if len(row) > 1}

def batch_update_sheet(worksheet, updates): # Renamed to avoid name conflict
    """Batch update Google Sheets with prepared updates."""
    if updates:
        worksheet.batch_update(updates)

def append_new_rows_sheet(worksheet, new_rows, selling_price_column_index, referral_fee_column_index, product_category_column_index, shipping_column_index, label_fee_column_index, processing_fee_column_index, profit_loss_column_index, sku_column_index, detail_columns_start_index): # Modified to accept new column indices and detail columns start
    """Append new rows and format price column with default value and background."""
    if new_rows:
        next_row = len(worksheet.get_all_values()) + 1
        # Prepare data for initial row insertion (excluding details_dict)
        rows_to_insert = [row[:-1] for row in new_rows] # Exclude the last element (details_dict) from each row
        worksheet.insert_rows(rows_to_insert, row=next_row)

        # --- Formatting and Default Values for New Columns ---

        # Selling Price (Column Z) - existing formatting
        price_range = f"{selling_price_column_index}{next_row}:{selling_price_column_index}{next_row + len(new_rows) - 1}"
        price_formatting = {
            "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"},
            "backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.7} # Light orange RGB
        }
        worksheet.format(price_range, price_formatting)

        # Referral Fee Percentage (Column Y) - existing formatting
        referral_fee_range = f"{referral_fee_column_index}{next_row}:{referral_fee_column_index}{next_row + len(new_rows) - 1}"
        referral_fee_formatting = {
            "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}, # Format as number with 2 decimals
             "backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.7} # Light orange RGB - Consistent background
        }
        worksheet.format(referral_fee_range, referral_fee_formatting)

        # Product Category (Column W) - Data Validation Removed

        # Label Fee (Column AA) - Default Value and Formatting
        label_fee_range = f"{label_fee_column_index}{next_row}:{label_fee_column_index}{next_row + len(new_rows) - 1}"
        worksheet.format(label_fee_range, {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}}) # Format as number
        worksheet.update(label_fee_range, [[DEFAULT_LABEL_FEE]] * len(new_rows)) # Set default value

        # Processing Fee (Column AB) - Default Value and Formatting
        processing_fee_range = f"{processing_fee_column_index}{next_row}:{processing_fee_column_index}{next_row + len(new_rows) - 1}"
        worksheet.format(processing_fee_range, {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}}) # Format as number
        worksheet.update(processing_fee_range, [[DEFAULT_PROCESSING_FEE]] * len(new_rows)) # Set default value

        # Profit/Loss (Column AC) - Formula (applied to all new rows)
        profit_loss_range = f"{profit_loss_column_index}{next_row}:{profit_loss_column_index}{next_row + len(new_rows) - 1}"
        profit_loss_formula = f"=(Y{next_row}+Z{next_row})-(E{next_row}+AA{next_row}+AB{next_row})" # Formula for the first row
        formula_values = [[profit_loss_formula]] * len(new_rows) # Repeat formula for all new rows
        worksheet.update(profit_loss_range, formula_values, value_input_option='USER_ENTERED') # Use USER_ENTERED to apply formula

        # SKU (Column A) - Value (generated SKU)
        sku_range = f"{sku_column_index}{next_row}:{sku_column_index}{next_row + len(new_rows) - 1}"
        sku_values = []
        for i in range(len(new_rows)): # Generate SKU for each new row
            product_id_val = new_rows[i][1] # Product ID is in the 2nd column (index 1) of new_rows
            price_val = new_rows[i][4]     # Price is in the 5th column (index 4) of new_rows
            sku = f"{product_id_val}-{price_val}-PK-WMPL" # Create SKU string
            sku_values.append([sku])
        worksheet.update(sku_range, sku_values)

        # --- Detail Column (AD - "Details") ---
        header_cell = f"{detail_columns_start_index}1" # Cell for "Details" header (e.g., AD1)
        header_row_values = worksheet.row_values(1)
        if 'Details' not in header_row_values:
            worksheet.update(header_cell, [['Details']]) # Set "Details" header in column AD

        for row_index, detail_data in enumerate(new_rows):
            details_dict = detail_data[-1] # Details Dictionary is now the *last* element of each row
            details_text_list = [] # List to store detail strings for concatenation

            for detail_pair in details_dict.get("AD values", []): # Iterate through detail pairs
                for detail_value in detail_pair: # Iterate through values in each pair
                    details_text_list.append(detail_value) # Add each detail value to the list

            combined_details_text = "\n".join(details_text_list) # Concatenate details with newline

            cell_range = f"{detail_columns_start_index}{next_row + row_index}" # Cell in "Details" column for current row
            worksheet.update(cell_range, [[combined_details_text]]) # Write concatenated details to "Details" column


# --- Main Script ---
def main():
    """Main function to process Excel data and update Google Sheets."""
    client = authenticate_gspread()
    worksheet = get_worksheet(client)

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[["Excel Files", "*.xlsx"]])

    if not file_path:
        print("No file selected.")
        return

    try:
        df = load_excel(file_path)
    except FileNotFoundError:
        print(f"Error: Excel file not found at '{file_path}'.")
        return
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return


    required_columns = ["web-scraper-start-url", "heading", "brand", "market_price", "images", "summary", "keyfeatures", "schema_org_breadcrumbs", "details"] # Added details column
    if not all(col in df.columns for col in required_columns):
        print("Required columns not found in the Excel file. Found columns:", df.columns.tolist())
        return

    df["product_id"] = df["web-scraper-start-url"].apply(extract_product_id)
    existing_product_ids = get_existing_product_ids(worksheet)

    updates = []
    new_rows = []

    # --- Header Row Updates with Explicit Columns ---
    header_row = worksheet.row_values(1)
    headers_to_update = {}
    if 'SKU' not in header_row:
        headers_to_update['A1'] = [['SKU']] # Column A for SKU
    if 'Product ID' not in header_row:
        headers_to_update['B1'] = [['Product ID']] # Column B for Product ID
    if 'Heading' not in header_row:
        headers_to_update['C1'] = [['Heading']]     # Column C for Heading
    if 'Brand' not in header_row:
        headers_to_update['D1'] = [['Brand']]       # Column D for Brand
    if 'Price' not in header_row:
        headers_to_update['E1'] = [['Price']]       # Column E for Price
    if 'Image 1' not in header_row:
        for idx, col_header in enumerate([f'Image {i+1}' for i in range(IMAGE_COLUMN_COUNT)]):
            headers_to_update[f'{chr(ord("F") + idx)}1'] = [[col_header]] # Columns F, G, H, I, J for Images
    if 'Summary' not in header_row:
        headers_to_update['K1'] = [['Summary']]     # Column K for Summary
    if 'Key Feature 1' not in header_row:
        headers_to_update['L1'] = [['Key Feature 1']] # Column L for Key Feature 1
    if 'Key Feature 2' not in header_row:
        headers_to_update['M1'] = [['Key Feature 2']] # Column M for Key Feature 2
    if 'Remaining Key Features' not in header_row:
        headers_to_update['N1'] = [['Remaining Key Features']] # Column N for Remaining Key Features
    # --- Category Headers ---
    if 'Category 1' not in header_row:
        headers_to_update['O1'] = [['Category 1']]   # Column O for Category 1
    if 'Category 2' not in header_row:
        headers_to_update['P1'] = [['Category 2']]   # Column P for Category 2
    if 'Category 3' not in header_row:
        headers_to_update['Q1'] = [['Category 3']]   # Column Q for Category 3
    if 'Category 4' not in header_row:
        headers_to_update['R1'] = [['Category 4']]   # Column R for Category 4
    if 'Category 1 URL' not in header_row:
        headers_to_update['S1'] = [['Category 1 URL']] # Column S for Category 1 URL
    if 'Category 2 URL' not in header_row:
        headers_to_update['T1'] = [['Category 2 URL']] # Column T for Category 2 URL
    if 'Category 3 URL' not in header_row:
        headers_to_update['U1'] = [['Category 3 URL']] # Column U for Category 3 URL
    if 'Category 4 URL' not in header_row:
        headers_to_update['V1'] = [['Category 4 URL']] # Column V for Category 4 URL
    # --- Product Category and Referral Fee Headers ---
    if 'Product Category' not in header_row:
        headers_to_update['W1'] = [['Product Category']] # Column W for Product Category
    if 'Referral Fee Percentage' not in header_row:
        headers_to_update['X1'] = [['Referral Fee Percentage']] # Column X for Referral Fee Percentage
    # --- Referral Fee Percentage and Selling Price Headers (Columns Y and Z) ---
    if 'Shipping' not in header_row:
        headers_to_update['Y1'] = [['Shipping']]      # Column Y for Shipping
    if 'Selling Price' not in header_row:
        headers_to_update['Z1'] = [['Selling Price']]   # Column Z for Selling Price
    # --- New Columns: Label Fee, Processing Fee, Profit/Loss ---
    if 'Label Fee' not in header_row:
        headers_to_update['AA1'] = [['Label Fee']]     # Column AA for Label Fee
    if 'Processing Fee' not in header_row:
        headers_to_update['AB1'] = [['Processing Fee']]    # Column AB for Processing Fee
    if 'Profit/Loss' not in header_row:
        headers_to_update['AC1'] = [['Profit/Loss']]     # Column AC for Profit/Loss
    # --- Details Column Header ---
    if 'Details' not in header_row:
        headers_to_update['AD1'] = [['Details']]       # Column AD for Details


    if headers_to_update:
        update_header_list = [{'range': cell, 'values': values} for cell, values in headers_to_update.items()]
        batch_update_sheet(worksheet, update_header_list)


    for _, row in df.iterrows():
        product_id = row.get("product_id", "").strip()
        numeric_price = extract_numeric_price(row.get("market_price", "")) # Use numeric price extraction
        selling_price = DEFAULT_SELLING_PRICE # Default selling price
        referral_fee_percentage_default = DEFAULT_REFERRAL_FEE # Default Referral Fee Percentage - unusual to set a fixed value
        image_urls = extract_images(row.get("images", "[]"))
        summary_text = extract_summary(row.get("heading", ""), row.get("summary", "")) # Extract summary
        key_feature_1, key_feature_2, remaining_key_features = extract_key_features(row.get("keyfeatures", "[]"), summary_text) # Extract key features
        category_names, category_urls = extract_categories(row.get("schema_org_breadcrumbs", "[]")) # Extract categories and URLs
        product_category = get_product_category(category_names, category_urls, row.get("heading", ""), summary_text) # Determine product category
        referral_fee_percentage = calculate_referral_fee(product_category, selling_price) # Calculate referral fee using selling price
        sku = f"{product_id}-{numeric_price}-PK-WMPL" # Generate SKU
        details_json_str = row.get('details', '[]') # Get details json string
        details_dict = extract_details_keyword_grouped(details_json_str) # Extract details using keyword function


        if product_id and product_id in existing_product_ids:
            sheet_row = existing_product_ids[product_id]
            updates.append({'range': f"E{sheet_row}", 'values': [[numeric_price]]}) # Column E: Update numeric price
            updates.append({'range': f"F{sheet_row}", 'values': [[image_urls[0] if len(image_urls) > 0 else ""]]}) # Column F: Image 1
            updates.append({'range': f"G{sheet_row}", 'values': [[image_urls[1] if len(image_urls) > 1 else ""]]}) # Column G: Image 2
            updates.append({'range': f"H{sheet_row}", 'values': [[image_urls[2] if len(image_urls) > 2 else ""]]}) # Column H: Image 3
            updates.append({'range': f"I{sheet_row}", 'values': [[image_urls[3] if len(image_urls) > 3 else ""]]}) # Column I: Image 4
            updates.append({'range': f"J{sheet_row}", 'values': [[image_urls[4] if len(image_urls) > 4 else ""]]}) # Column J: Image 5
            updates.append({'range': f"K{sheet_row}", 'values': [[summary_text]]}) # Column K: Update Summary
            updates.append({'range': f"L{sheet_row}", 'values': [[key_feature_1]]}) # Column L: Update Key Feature 1
            updates.append({'range': f"M{sheet_row}", 'values': [[key_feature_2]]}) # Column M: Update Key Feature 2
            updates.append({'range': f"N{sheet_row}", 'values': [[remaining_key_features]]}) # Column N: Update Remaining Key Features
            # --- Category Updates ---
            updates.append({'range': f"O{sheet_row}", 'values': [[category_names[0]]]}) # Column O: Category 1
            updates.append({'range': f"P{sheet_row}", 'values': [[category_names[1]]]}) # Column P: Category 2
            updates.append({'range': f"Q{sheet_row}", 'values': [[category_names[2]]]}) # Column Q: Category 3
            updates.append({'range': f"R{sheet_row}", 'values': [[category_names[3]]]}) # Column R: Category 4
            # --- Category URL Updates ---
            updates.append({'range': f"S{sheet_row}", 'values': [[category_urls[0]]]}) # Column S: Category 1 URL
            updates.append({'range': f"T{sheet_row}", 'values': [[category_urls[1]]]}) # Column T: Category 2 URL
            updates.append({'range': f"U{sheet_row}", 'values': [[category_urls[2]]]}) # Column U: Category 3 URL
            updates.append({'range': f"V{sheet_row}", 'values': [[category_urls[3]]]}) # Column V: Category 4 URL
            # --- Product Category and Referral Fee Updates ---
            updates.append({'range': f"W{sheet_row}", 'values': [[product_category]]}) # Column W: Product Category
            updates.append({'range': f"X{sheet_row}", 'values': [[referral_fee_percentage]]}) # Column X: Referral Fee Percentage
            # --- Referral Fee Percentage and Selling Price Updates (No color change for existing) ---
            updates.append({'range': f"Y{sheet_row}", 'values': [[DEFAULT_REFERRAL_FEE]]}) # Column Y: Shipping (Actually Referral Fee Percentage Default as per previous request)
            updates.append({'range': f"Z{sheet_row}", 'values': [[selling_price]]}) # Column Z: Selling Price (Default for existing, no color change)
            # --- New Columns (No updates for existing rows in this version) ---


        else:
            new_rows.append([
                sku,                  # Column A: SKU (generated)
                int(product_id),          # Column B: Product ID
                row.get("heading", ""),     # Column C: Heading
                get_random_brand(),       # Column D: Brand
                numeric_price,           # Column E: Price
                image_urls[0] if len(image_urls) > 0 else "",  # Column F: Image 1
                image_urls[1] if len(image_urls) > 1 else "",  # Column G: Image 2
                image_urls[2] if len(image_urls) > 2 else "",  # Column H: Image 3
                image_urls[3] if len(image_urls) > 3 else "",  # Column I: Image 4
                image_urls[4] if len(image_urls) > 4 else "",  # Column J: Image 5
                summary_text,              # Column K: Summary
                key_feature_1,          # Column L: Key Feature 1
                key_feature_2,          # Column M: Key Feature 2
                remaining_key_features,    # Column N: Remaining Key Features
                category_names[0],           # Column O: Category 1
                category_names[1],           # Column P: Category 2
                category_names[2],           # Column Q: Category 3
                category_names[3],            # Column R: Category 4
                category_urls[0],            # Column S: Category 1 URL
                category_urls[1],            # Column T: Category 2 URL
                category_urls[2],            # Column U: Category 3 URL
                category_urls[3],             # Column V: Category 4 URL
                product_category,          # Column W: Product Category
                referral_fee_percentage,     # Column X: Referral Fee Percentage
                DEFAULT_REFERRAL_FEE,      # Column Y: Shipping (Actually Referral Fee Percentage Default)
                DEFAULT_SELLING_PRICE,       # Column Z: Selling Price
                DEFAULT_LABEL_FEE,         # Column AA: Label Fee (Default Value)
                DEFAULT_PROCESSING_FEE,    # Column AB: Processing Fee (Default Value)
                "",                      # Column AC: Profit/Loss (Formula will be set in append_new_rows_sheet)
                details_dict               # Column AD onwards: details_dict
            ])

    batch_update_sheet(worksheet, updates)
    if updates:
        print("Existing product data successfully updated in Google Sheets.")

    if new_rows:
        print("Data being appended to sheet (new_rows):")
        for row in new_rows:
            print(row)
        selling_price_column_index = 'Z' # Column Z index
        referral_fee_column_index = 'Y' # Column Y index
        product_category_column_index = 'W' # Column W index
        shipping_column_index = 'Y'      # Column Y index - Shipping (Though actually Referral Fee Percentage Default)
        label_fee_column_index = 'AA'      # Column AA index
        processing_fee_column_index = 'AB' # Column AB index
        profit_loss_column_index = 'AC'      # Column AC index
        sku_column_index = 'A'          # Column A index
        detail_columns_start_index_char = 'AD' # Start of detail columns

        append_new_rows_sheet(worksheet, new_rows, selling_price_column_index, referral_fee_column_index, product_category_column_index, shipping_column_index, label_fee_column_index, processing_fee_column_index, profit_loss_column_index, sku_column_index, detail_columns_start_index=detail_columns_start_index_char) # Pass detail_columns_start_index


    if new_rows:
        print("New product data appended to Google Sheets.")
    else:
        print("No new products to append.")


if __name__ == '__main__':
    main()