# save as app.py
import streamlit as st
import requests
import pandas as pd
from base64 import b64encode

# --- User Input ---
st.title("eBay Used Cars Under $5,000")
max_price = st.slider("Select max price", 1000, 10000, 5000, step=500)
make = st.text_input("Car make (e.g., Toyota, Honda)", value="Toyota")

# --- Credentials ---
client_id = st.secrets["EBAY_CLIENT_ID"]
client_secret = st.secrets["EBAY_CLIENT_SECRET"]

# --- Token Retrieval ---
def get_ebay_token(client_id, client_secret):
    auth_header = b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_header}'
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    response = requests.post('https://api.ebay.com/identity/v1/oauth2/token', headers=headers, data=data)
    return response.json()['access_token']

# --- Search Function ---
def search_cars(token, make, max_price):
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'q': f'{make} used car',
        'filter': f'price:[0..{max_price}]',
        'limit': 25,
        'category_ids': '6001',
        'sort': 'price'
    }
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    r = requests.get(url, headers=headers, params=params)
    return r.json().get("itemSummaries", [])

# --- Display Results ---
if st.button("Search"):
    token = get_ebay_token(client_id, client_secret)
    results = search_cars(token, make, max_price)

    if results:
        df = pd.DataFrame([{
            "Title": x.get("title"),
            "Price": f"${x['price']['value']}",
            "Condition": x.get("condition"),
            "Location": x.get("itemLocation", {}).get("city", ""),
            "URL": x.get("itemWebUrl")
        } for x in results])
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), file_name="ebay_cars.csv")
    else:
        st.warning("No results found.")

