from flask import Flask, render_template, request, redirect, url_for
import pickle
import pandas as pd
import requests

# Initialize the Flask application
app = Flask(__name__)

# Load the data and similarity matrix
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDB API Poster Fetch Function
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return None

# Function to recommend movies
def recommend(movie):
    movie = movie.lower()
    movie_matches = movies[movies['title'].str.lower() == movie]
    
    if movie_matches.empty:
        return None, None
    
    movie_index = movie_matches.index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        # Fetch movie poster
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movie_posters

# Flask route for home page with search form
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle recommendation based on search input
@app.route('/recommend', methods=['POST'])
def recommend_movies():
    selected_movie = request.form['movie_name']
    
    # Recommend movies based on the searched movie
    recommendations, posters = recommend(selected_movie)
    
    if recommendations is None:
        # If the movie is not found, redirect back to home with an error message
        return redirect(url_for('index', not_found=True))

    # Combine recommendations and posters into a list of tuples
    recommended_movies_data = zip(recommendations, posters)

    return render_template('recommend.html', selected_movie=selected_movie, recommended_movies_data=recommended_movies_data)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
