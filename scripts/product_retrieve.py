import requests
import base64
import random
import json
import csv
import pandas as pd

# Walmart API credentials
client_id = "34516130-2a5b-459b-9bbd-eeb7a2444d40"
client_secret = "OZHf14iHvDWIkpqarvQjCiVfyu2dD_nbf62hh3QcumKeuLIaphNrEsH9og8XPuqeojPdOeDnkEA7UhC8C1DCCQ"
consumer_id = str(random.randint(100000, 999999))  # Generate a random consumer ID
channel_type = str(random.randint(1000, 9999))  # Generate a random channel type

def get_walmart_access_token(client_id, client_secret):
    url = "https://marketplace.walmartapis.com/v3/token"
    
    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "WM_SVC.NAME": "Walmart Marketplace",
        "WM_QOS.CORRELATION_ID": str(random.randint(1000000000, 9999999999)),
        "WM_SVC.VERSION": "1.0.0",
        "WM_CONSUMER.CHANNEL.TYPE": channel_type
    }
    
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get token: {response.text}")

def search_walmart_products(query):
    access_token = get_walmart_access_token(client_id, client_secret)
    url = f"https://marketplace.walmartapis.com/v3/items/walmart/search?query={query}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "WM_SVC.NAME": "Walmart Marketplace",
        "WM_QOS.CORRELATION_ID": str(random.randint(1000000000, 9999999999)),
        "WM_CONSUMER.CHANNEL.TYPE": channel_type,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve product info: {response.text}")

def extract_products_from_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        return [item["productId"] for item in data]

def save_to_excel(products, output_file="walmart_products.xlsx"):
    df = pd.DataFrame(products)
    df.to_excel(output_file, index=False)
    print(f"Product information saved to {output_file}")

# Load product IDs from tide.json
product_ids = extract_products_from_json("tide.json")
product_details = []

for product_id in product_ids:
    try:
        product_info = search_walmart_products(product_id)
        product_details.append(product_info)
    except Exception as e:
        print(f"Error retrieving product {product_id}: {e}")

# Save product details to Excel
save_to_excel(product_details)