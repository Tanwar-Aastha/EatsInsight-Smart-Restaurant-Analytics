import streamlit as st

import streamlit as st
import pickle 
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


st.set_page_config(page_title='Restaurant Recommender')

# Creating a recommendation system based on the country, city, cuisines and price range
df = pd.read_csv('task-2/final_data.csv')
    

# Fit TF-IDF on entire dataset (before filtering)
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Cuisines'].fillna(""))

# Mapping currency symbols for cost
currency_symbols = {
   'Indian Rupees(Rs.)' : '₹',      
    'Dollar($)':'$' ,                 
    'Pounds(£)':'£',                  
    'Brazilian Real(R$)': 'R$',       
    'Rand(R)': 'R',            
    'Emirati Diram(AED)': 'د.إ',          
    'NewZealand($)': '$',           
    'Turkish Lira(TL)': 'TL',            
    'Botswana Pula(P)': 'P',        
    'Indonesian Rupiah(IDR)' :'Rp',     
    'Qatari Rial(QR)': 'QR',             
    'Sri Lankan Rupee(LKR)':'Rs' 
}

# Function to Format Cost with Currency Symbol
def format_cost(row):
    currency_symbol = currency_symbols.get(row['Currency'], row['Currency'])  # Get symbol or default to currency name
    return f"{currency_symbol}{row['Cost']}"
    

# Function to Recommend Restaurants
def restaurant_recommender(country, city, preferred_cuisines, price_range, top_n=5):
    # Filter by Country and City
    filtered_df = df[(df['Country'] == country) & (df['City'] == city)].copy()
    
    if filtered_df.empty:
        return "No restaurants found for the selected location."
    
    # Normalize Price Range
    scaler = StandardScaler()
    price_normalized = scaler.fit_transform(filtered_df[['Price range']])
    
    # Compute Similarity for Price Range
    price_sim = cosine_similarity(price_normalized)

    # Convert Selected Cuisines to TF-IDF Format
    preferred_cuisines = ' '.join(preferred_cuisines)  # Convert list to string
    input_vector = tfidf_vectorizer.transform([preferred_cuisines])

    # Compute Cosine Similarity for Cuisines
    input_cuisine_sim = cosine_similarity(input_vector, tfidf_matrix[df.index.isin(filtered_df.index)]).flatten()

    # Store Similarity Scores in Filtered DataFrame
    filtered_df['Cuisine Similarity'] = input_cuisine_sim
    filtered_df['Price Similarity'] = price_sim.diagonal()

    # Normalize Ratings (Higher Rating = More Recommended)
    filtered_df['Normalized Rating'] = filtered_df['Rating'] / filtered_df['Rating'].max()

    # Compute Final Score (Weighted)
    filtered_df['Final Score'] = (filtered_df['Cuisine Similarity'] * 0.5) + (filtered_df['Price Similarity'] * 0.2) + (filtered_df['Normalized Rating'] * 0.3)

    # Get Top N Recommendations
    recommendations = filtered_df.sort_values(by='Final Score', ascending=False).head(top_n)
    
    # Format Cost Column
    recommendations['Cost'] = recommendations.apply(format_cost, axis=1)

    return recommendations[['Name', 'Address', 'Cost', 'Rating']]




st.title('Restaurant Recommender')

st.subheader('Select the Options below:')

# Selecting Country
select_country = st.selectbox('Country', df['Country'].unique())

# Filtering Cities based on selected Country
filtered_cities = df[df['Country'] == select_country]['City'].unique()
select_city = st.selectbox('City', filtered_cities)

# Selecting Price Range
price_range_mapping = {
    'Affordable':1, 'Casual Dining':2,'Premium':3, 'Luxury Dining':4
}
select_price_range = st.selectbox('Price Range', list(price_range_mapping.keys()))
price_range_value = price_range_mapping[select_price_range]


# Selecting Cuisines (Multiselect)
all_cuisines = sorted(set(', '.join(df['Cuisines']).split(', ')))  # Extract unique cuisines
select_cuisines = st.multiselect('Select Cuisines', all_cuisines)

if st.button('Search'):
    recommend_df = restaurant_recommender(select_country, select_city, select_cuisines, select_price_range)
    st.dataframe(recommend_df)

