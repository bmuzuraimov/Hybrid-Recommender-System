from flask import Blueprint, render_template, request

# Import custom utility modules
from .tools.data_tool import load_data
from .utils import get_courses_by_preference, get_recommendation_by_content_based_filtering, get_liked_similar_by, get_user_likes_by, parse_cookie

# Initialize the Blueprint
bp = Blueprint('main', __name__, url_prefix='/')

# Load initial data
courses, category, subcategories, price_ranges, num_lectures_ranges, content_length_minutes_ranges = load_data()

@bp.route('/', methods=('GET', 'POST'))
def index():
    # Convert database query results to dictionaries
    default_category = category.to_dict('records')
    default_subcategories = subcategories.to_dict('records')
    default_price_ranges = price_ranges.to_dict('records')
    default_num_lectures_ranges = num_lectures_ranges.to_dict('records')
    default_content_length_minutes_ranges = content_length_minutes_ranges.to_dict('records')

    # Retrieve user preferences from cookies
    user_category = parse_cookie(request.cookies.get('user_category'))
    user_subcategory = parse_cookie(request.cookies.get('user_subcategory'))
    user_price_ranges = parse_cookie(request.cookies.get('user_price_ranges'))
    user_num_lectures_ranges = parse_cookie(request.cookies.get('user_num_lectures_ranges'))
    user_content_length_minutes_ranges = parse_cookie(request.cookies.get('user_content_length_minutes_ranges'))
    user_rates = parse_cookie(request.cookies.get('user_rates'))
    user_likes = parse_cookie(request.cookies.get('user_likes'), int)

    # Fetch courses based on the default category and user preferences
    default_category_courses = get_courses_by_preference(courses, user_category, user_subcategory)[:12]
    # Get recommendations based on user ratings
    recommendations_courses, recommendations_message = get_recommendation_by_content_based_filtering(courses, user_rates, user_likes)

    # Get courses similar to those liked by the user
    likes_similar_courses, likes_similar_message = get_liked_similar_by(courses, user_likes)
    
    # Get courses directly liked by the user
    likes_courses = get_user_likes_by(courses, user_likes)
    
    # Render the template with all data prepared
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
