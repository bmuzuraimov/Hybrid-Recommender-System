from flask import (
    Blueprint, render_template, request
)

from .tools.data_tool import *
from .utils import *



bp = Blueprint('main', __name__, url_prefix='/')

movies, genres, rates = loadData()

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

@bp.route('/', methods=('GET', 'POST'))
def index():

    # Default Genres List
    default_genres = genres.to_dict('records')[:-1]

    # User Genres
    user_genres = request.cookies.get('user_genres')
    if user_genres:
        user_genres = user_genres.split(",")
    else:
        user_genres = []

    # User Rates
    user_rates = request.cookies.get('user_rates')
    if user_rates:
        user_rates = user_rates.split(",")
    else:
        user_rates = []

    # User Likes
    user_likes = request.cookies.get('user_likes')
    if user_likes:
        user_likes = user_likes.split(",")
    else:
        user_likes = []

    default_genres_movies = getMoviesByGenres(movies, genres, user_genres)[:12]
    recommendations_movies, recommendations_message = getRecommendationBy(movies, rates, user_rates)
    likes_similar_movies, likes_similar_message = getLikedSimilarBy(movies, [int(numeric_string) for numeric_string in user_likes])
    likes_movies = getUserLikesBy(movies, user_likes)
    return render_template('index.html',
                           genres=default_genres,
                           user_genres=user_genres,
                           user_rates=user_rates,
                           user_likes=user_likes,
                           default_genres_movies=default_genres_movies,
                           recommendations=recommendations_movies,
                           recommendations_message=recommendations_message,
                           likes_similars=likes_similar_movies,
                           likes_similar_message=likes_similar_message,
                           likes=likes_movies,
                           )