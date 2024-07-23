import streamlit as st
import pandas as pd
import pickle
import requests
import os

def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        response.raise_for_status()  # Check if request was successful
        data = response.json()
        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return poster_url
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return None

def reassemble_files(output_path, input_pattern, num_parts):
    if not os.path.exists(output_path):
        with open(output_path, 'wb') as output_file:
            for i in range(num_parts):
                chunk_path = f'{input_pattern}.part{i}'
                if os.path.exists(chunk_path):
                    with open(chunk_path, 'rb') as chunk_file:
                        output_file.write(chunk_file.read())
                else:
                    st.error(f"Chunk file {chunk_path} not found.")
                    return

# Reassemble similarity.pkl
reassemble_files('similarity.pkl', 'similarity.pkl', 7)

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = list(enumerate(similarity[movie_index]))
    distances_sorted = sorted(distances, reverse=True, key=lambda x: x[1])
    return distances_sorted

# Title
st.title('Movie Recommender System')

# User input for movie selection
selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    movies_recommended = recommend(selected_movie_name)
    names = []
    images = []

    # Loop through recommended movies
    for i in movies_recommended[:11]:  # Limit to top 6 recommendations
        if movies.iloc[i[0]]['title'] != selected_movie_name:
            movie_id = movies.iloc[i[0]]['movie_id']  # Adjust if your DataFrame column name is different
            image_url = fetch_poster(movie_id)
            if image_url:  # Check if URL is valid
                images.append(image_url)
                names.append(movies.iloc[i[0]]['title'])

    if names:
        cols1 = st.columns(5)
        cols2 = st.columns(5)

        for col, name, image in zip(cols1, names[:5], images[:5]):
            with col:
                st.text(name)
                st.image(image)

        for col, name, image in zip(cols2, names[5:10], images[5:10]):
            with col:
                st.text(name)
                st.image(image)
    else:
        st.write("No recommendations available.")
