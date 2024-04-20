from flask import (
    Blueprint, render_template, request
)

from .tools.data_tool import *
from .utils import *



bp = Blueprint('main', __name__, url_prefix='/')

courses, category, subcategories, price_ranges, num_lectures_ranges, content_length_minutes_ranges = loadData()

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

@bp.route('/', methods=('GET', 'POST'))
def index():

    # Default Category List
    default_category = category.to_dict('records')
    default_subcategories = subcategories.to_dict('records')
    default_price_ranges = price_ranges.to_dict('records')
    default_num_lectures_ranges = num_lectures_ranges.to_dict('records')
    default_content_length_minutes_ranges = content_length_minutes_ranges.to_dict('records')

    # User Category
    user_category = request.cookies.get('user_category')
    if user_category:
        user_category = user_category.split(",")
    else:
        user_category = []

    # User Subcategory
    user_subcategory = request.cookies.get('user_subcategory')
    if user_subcategory:
        user_subcategory = user_subcategory.split(",")
    else:
        user_subcategory = []

    # Price Ranges
    user_price_ranges = request.cookies.get('user_price_ranges')
    if user_price_ranges:
        user_price_ranges = user_price_ranges.split(",")
    else:
        user_price_ranges = []

    # Num Lectures Ranges
    user_num_lectures_ranges = request.cookies.get('user_num_lectures_ranges')
    if user_num_lectures_ranges:
        user_num_lectures_ranges = user_num_lectures_ranges.split(",")
    else:
        user_num_lectures_ranges = []
    
    # Content Length Minutes Ranges
    user_content_length_minutes_ranges = request.cookies.get('user_content_length_minutes_ranges')
    if user_content_length_minutes_ranges:
        user_content_length_minutes_ranges = user_content_length_minutes_ranges.split(",")
    else:
        user_content_length_minutes_ranges = []

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

    default_category_courses = getCoursesByCategory(courses, category, subcategories, price_ranges, num_lectures_ranges, content_length_minutes_ranges, user_category, user_subcategory, user_price_ranges, user_num_lectures_ranges, user_content_length_minutes_ranges)[:12]
    recommendations_courses, recommendations_message = getRecommendationBy(courses, user_rates)
    likes_similar_courses, likes_similar_message = getLikedSimilarBy(courses, [int(numeric_string) for numeric_string in user_likes])
    likes_courses = getUserLikesBy(courses, user_likes)
    return render_template('index.html',
                           category=default_category,
                           subcategory=default_subcategories,
                           price_ranges=default_price_ranges,
                           num_lectures_ranges=default_num_lectures_ranges,
                           content_length_minutes_ranges=default_content_length_minutes_ranges,
                           user_category=user_category,
                           user_subcategory=user_subcategory,
                           user_price_ranges=user_price_ranges,
                           user_num_lectures_ranges=user_num_lectures_ranges,
                           user_content_length_minutes_ranges=user_content_length_minutes_ranges,
                           user_rates=user_rates,
                           user_likes=user_likes,
                           default_category_courses=default_category_courses,
                           recommendations=recommendations_courses,
                           recommendations_message=recommendations_message,
                           likes_similars=likes_similar_courses,
                           likes_similar_message=likes_similar_message,
                           likes=likes_courses,
                           )