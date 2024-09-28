import streamlit as st
import pandas as pd
import random
from collections import Counter
from faker import Faker
from transformers import pipeline
import hashlib
import os

# Initialize Faker for generating fake user data
fake = Faker()

# Initialize DistilGPT-2 pipeline for generating personalized offer descriptions
generator = pipeline('text-generation', model='distilgpt2')

# Define the merchant list by subcategory
subcategory_merchants = {
    "flights": ["Anasa Airways", "SkyHigh Flights", "JetStream Airlines"],
    "accommodations": ["Nivasa Hotels", "Comfort Suites", "StayEasy Inn"],
    "travel aggregators": ["Pagoda", "TravelGenie", "TripHopper"],
    "theatres": ["Zinox Theatres", "CineMagic", "FilmWorld Cinemas"],
    "amusement parks": ["Inagica Water Park", "FunLand", "Adventure Park"],
    "restaurants": ["Gourmet Bistro", "Foodie Haven", "TasteBud Café"],
    "delivery services": ["Zwiggy", "FoodPanda", "Deliveroo"],
    "supermarkets": ["Kirandeep Supermarket", "Grocery Mart", "FreshFare"],
    "electronic stores": ["Nichroma", "TechStore", "GadgetHub"],
    "electronic appliance brands": ["HomeTech Appliances", "SmartHome", "ElectroWorld"],
    "online shopping stores": ["Blipkart", "Shopify", "E-Mall"],
    "pharmacy": ["Health Plus", "MediMart", "Wellness Pharmacy"],
    "hospitals": ["CareMax Hospital", "HealthFirst Clinic", "City Hospital"],
    "jewellery": ["Luxury Jewels", "Elegant Designs", "Jewels & Gems"],
    "high-end goods": ["Exclusive Goods Store", "Prestige Items", "Luxury Boutique"],
    "watches": ["Timeless Watches", "Elite Timepieces", "Watch World"],
    "educational websites": ["LearnOnline", "EduPortal", "SkillUp"],
    "softwares": ["SoftWare Pro", "CodeMasters", "DevTools"],
    "frameworks": ["Tech Frameworks", "CodeLibs", "Framework Depot"]
}

# Define the credit card offers
credit_card_offers = {
    "Travel and Entertainment": {
        "flights": "Get 20% off on your flight booking!",
        "accommodations": "Get a free day of hotel stay!",
        "travel aggregators": "Get up to 10% cashback!",
        "theatres": "Get free tickets on your next movie visit!",
        "amusement parks": "Buy 1 get 1 at your favourite water park!"
    },
    "Dining and Groceries": {
        "restaurants": "Enjoy a gourmet dining experience!",
        "delivery services": "Get free dessert with your next delivery!",
        "supermarkets": "Save 5% on your grocery bill!"
    },
    "Electronics and Gadgets": {
        "electronic stores": "Exclusive Rs999 worth of gadgets at Rs450!",
        "electronic appliance brands": "Get huge discounts on appliances!"
    },
    "Online Shopping": {
        "online shopping stores": "Get a free voucher on your next purchase!",
        "electronic stores": "Claim your Tech Shopper's Card!"
    },
    "Healthcare": {
        "pharmacy": "Receive exclusive discounts on your medications!",
        "hospitals": "Protect your health with our Health Protection Card!"
    },
    "Luxury and Jewelry": {
        "jewellery": "Luxury Jewelry rewards just for you!",
        "high-end goods": "Get exclusive high-end luxury items!",
        "watches": "Claim your premium watch offer!"
    },
    "Education and Learning": {
        "educational websites": "E-learning cards with free resources!",
        "softwares": "Get exclusive courses with Dorsera signup!",
        "frameworks": "Tech Framework cashback!"
    }
}

# Function to hash data (like names) securely
def hash_data(data):
    # Generate a random salt
    salt = os.urandom(16)
    
    # Create a hash object using SHA-256
    hash_object = hashlib.sha256()
    
    # Update the hash object with the data and the salt
    hash_object.update(salt + data.encode('utf-8'))
    
    # Return the salt and hashed value as a tuple
    return salt, hash_object.hexdigest()

# Function to generate fake transaction data with both original and hashed names
def generate_fake_data(n):
    data = []
    for _ in range(n):
        name = fake.name()
        
        # Hash the user's name
        salt, hashed_name = hash_data(name)
        
        age = random.randint(18, 65)
        gender = random.choice(["Male", "Female"])
        date = fake.date_this_year()  # Random date this year
        transactions = []
        for _ in range(50):
            subcategory = random.choice(list(subcategory_merchants.keys()))
            merchant = random.choice(subcategory_merchants[subcategory])
            transactions.append((subcategory, merchant))
        data.append({
            "original_name": name,  # Store the original name
            "hashed_name": hashed_name,  # Store the hashed name
            "salt": salt,  # Keep the salt for potential future use
            "age": age,
            "gender": gender,
            "date": date,
            "transactions": transactions
        })
    return data

# Function to count merchants by subcategory and category
def count_merchants(transactions):
    subcategory_count = Counter()
    category_count = Counter()
    for subcategory, merchant in transactions:
        subcategory_count[subcategory] += 1
        # Get category from subcategory
        for category, subcat_dict in credit_card_offers.items():
            if subcategory in subcat_dict:
                category_count[category] += 1
    return subcategory_count, category_count

# Function to get top subcategories and categories for a specific user
def get_top_categories_and_subcategories(subcategory_count, category_count):
    top_categories = category_count.most_common(3)
    top_subcategories = subcategory_count.most_common(4)
    return top_categories, top_subcategories

# Function to get 4 offers for a specific user from their top categories and highest subcategories
def get_appropriate_offers(original_name, age, top_categories, subcategory_count):
    offers = []
   
    # Loop through each top category (2 categories max)
    for category, _ in top_categories:
        # Apply age limit to Education and Learning category
        if category == "Education and Learning" and not (18 <= age <= 24):
            continue  # Skip Education offers if age not in the range

        # Get the subcategories that fall under this category
        subcategories_in_category = [
            (subcategory, count) for subcategory, count in subcategory_count.items()
            if subcategory in credit_card_offers[category]
        ]
        # Sort and take the top subcategories based on their count
        top_subcategories = sorted(subcategories_in_category, key=lambda x: -x[1])[:2]
       
        # Add predefined offers for each top subcategory
        for subcategory, _ in top_subcategories:
            offer = credit_card_offers[category][subcategory]
            offers.append(f"{category} ({subcategory}): {offer}")
       
        # Limit to 2 offers per category (4 offers total from 2 categories)
        if len(offers) >= 4:
            break

    return offers[:4]  # Ensure only 4 offers are returned

# Streamlit app
st.title("Credit Card Offer Finder")

# Generate and store data if not already in session state
if 'data' not in st.session_state:
    st.session_state['data'] = generate_fake_data(20)

data = st.session_state['data']

# Dropdown to select user for classification (display the original and hashed names)
user_choice = st.selectbox("Select a user to classify", [f"{user['original_name']} (Hashed: {user['hashed_name']})" for user in data])

# Extract the original name from the user_choice selection
selected_original_name = user_choice.split(" (Hashed: ")[0]

# Update the selected user in session state to prevent reloading the entire table
if 'selected_user' not in st.session_state or st.session_state['selected_user'] != selected_original_name:
    st.session_state['selected_user'] = selected_original_name

# Find the selected user by original name
selected_user = next(user for user in data if user["original_name"] == st.session_state['selected_user'])

# Flatten the transaction history for each user to display the table
flattened_data = [{
    "Original Name": selected_user["original_name"],
    "Hashed Name": selected_user["hashed_name"],
    "Age": selected_user["age"],
    "Gender": selected_user["gender"],
    "Subcategory": txn[0],
    "Merchant": txn[1]
} for txn in selected_user["transactions"]]

df = pd.DataFrame(flattened_data)
st.dataframe(df, height=400)

# Function to display classification results without column name duplication
if st.button("Classify Transactions for Selected User"):
    subcategory_count, category_count = count_merchants(selected_user["transactions"])
    top_categories, top_subcategories = get_top_categories_and_subcategories(subcategory_count, category_count)
    
    st.write(f"Top Categories for {selected_user['original_name']} (Hashed: {selected_user['hashed_name']}):")
    st.table({
        "Category": [category for category, _ in top_categories],
        "Subcategory": [subcategory for subcategory, _ in top_subcategories]
    })

    # Get and display personalized offers
    offers = get_appropriate_offers(selected_user['original_name'], selected_user['age'], top_categories, subcategory_count)
    st.write(f"Personalized Offers for {selected_user['original_name']} (Hashed: {selected_user['hashed_name']}):")
    for offer in offers:
        st.write(offer)
