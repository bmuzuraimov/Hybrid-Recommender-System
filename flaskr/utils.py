import pandas as pd
from .tools.data_tool import (
    ratesFromUser,
    get_categories,
    get_sub_categories,
    get_price_ranges,
    get_num_lectures_ranges,
    get_content_length_minutes_ranges,
    get_similarity_matrices,
    get_bin2vec_mappings
)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

rootPath = os.path.abspath(os.getcwd())

categories = get_categories()
subcategories = get_sub_categories()
price_ranges = get_price_ranges()
num_lectures_ranges = get_num_lectures_ranges()
content_length_minutes_ranges = get_content_length_minutes_ranges()

def get_user_likes_by(courses, user_likes):
    if not user_likes:
        return []

    # Convert user_likes to integer, in case they're not
    user_likes = [int(id) for id in user_likes]

    # Filter courses based on user likes (assuming 'id' is the index)
    results = courses.loc[courses.index.intersection(user_likes)]

    # Reorder the results according to the order in user_likes
    # Map the order of user_likes to the DataFrame index
    order_dict = {id: index for index, id in enumerate(user_likes)}
    results['order'] = results.index.map(order_dict)
    ordered_results = results.sort_values('order').drop('order', axis=1)
    # Return the results in the expected format
    return ordered_results.reset_index().to_dict('records') if not ordered_results.empty else []


def get_user_vectors(user_ids, reference_df, similarity_matrix):
    mask = reference_df['id'].isin([int(id) for id in user_ids])
    total_sum = np.sum(similarity_matrix[mask], axis=0)
    if np.max(total_sum) == np.min(total_sum):
        return np.zeros_like(total_sum)
    else:
        user_vector = (total_sum - np.min(total_sum)) / (np.max(total_sum) - np.min(total_sum))
        user_vector[np.isnan(user_vector)] = 0
        return user_vector


def calculate_similarity(courses_df, user_preference_vector):
    courses_copy_df = courses_df.copy()
    courses_copy_df['similarity'] = courses_copy_df['profile'].apply(lambda x: np.dot(x, user_preference_vector))
    # user cosine similarity
    # course_rep_matrix = np.stack(courses_copy_df['profile'].values)
    # similarity_matrix = cosine_similarity(user_preference_vector.reshape(1, -1), course_rep_matrix)
    # courses_copy_df['similarity'] = similarity_matrix[0]

    return courses_copy_df[courses_copy_df['similarity'] > 0.3]

def filter_top_courses(courses_df, num_top_courses=30):
    return courses_df.nlargest(num_top_courses, 'similarity')

def get_courses_by_preference(courses, user_category, user_subcategory):
    if not user_category and not user_subcategory:
        return []

    category_similarity_matrix, subcategory_similarity_matrix = get_similarity_matrices()
    user_category_vector = get_user_vectors(user_category, categories, category_similarity_matrix)
    user_subcategory_vector = get_user_vectors(user_subcategory, subcategories, subcategory_similarity_matrix)

    user_preference_vector = np.concatenate([user_category_vector, user_subcategory_vector, np.zeros(29)])

    courses = calculate_similarity(courses, user_preference_vector)
    results = filter_top_courses(courses)

    if not results.empty:
        return results.reset_index().to_dict('records')
    return []


def get_recommendation_by_content_based_filtering(courses, user_rates, user_likes):
    if not user_rates:
        return [], "No ratings provided."
    
    # Create data from user rates
    user_rates_df = ratesFromUser(user_rates)
    # drop rows that have lower than 3 ratings
    user_rates_df = user_rates_df[user_rates_df['rating'] >= 3]
    # get courses that have similar id with user rates
    user_rates_df = user_rates_df.merge(
        courses, left_on='id', right_on='id', how='inner')
    user_rates_df['profile'] = (
        5/user_rates_df['rating']) * user_rates_df['profile']
    profile = user_rates_df['profile'].mean()

    courses['similarity'] = courses['profile'].apply(
        lambda x: np.dot(x, profile))
    # ommit courses that have similarity score of 0
    courses = courses[courses['similarity'] > 0]
    courses = courses[~courses.index.isin(user_rates_df['id'])]
    courses = courses[~courses.index.isin(user_likes)]
    recommended_courses = courses[courses['similarity'] > 0].nlargest(
        20, 'similarity')

    if not recommended_courses.empty:
        return recommended_courses.reset_index().to_dict('records'), "These courses are recommended based on your ratings."
    return [], "No recommendations."


def get_liked_similar_by(courses, user_likes):
    results = []

    if len(user_likes) > 0:
        # Assuming 'courses' is a DataFrame with 'profile' being a column of arrays or list
        user_profile = courses.loc[courses.index.isin(
            user_likes), 'profile'].sum(axis=0)
        # normalize the user profile
        user_profile = user_profile / np.linalg.norm(user_profile)
        courses = courses[~courses.index.isin(user_likes)]
        course_rep_matrix = np.stack(
            courses['profile'].values)  # Stack arrays row-wise

        results = _generate_recommendation_results(
            user_profile, course_rep_matrix, courses, 10)
    if len(results) > 0:
        return results.reset_index().to_dict('records'), "The courses are similar to your liked courses."
    return [], "No similar courses found."


def _generate_recommendation_results(user_profile, item_rep_matrix, courses_data, k=12):
    # Ensure the user_profile is a 2D array with shape (1, number of features)
    user_profile_reshaped = user_profile.reshape(1, -1)
    # item_rep_matrix should already be in shape (number of courses, number of features)

    # Compute the cosine similarity
    recommendation_table = cosine_similarity(
        user_profile_reshaped, item_rep_matrix)

    # Convert similarity scores to a DataFrame column
    recommendation_table_df = courses_data.copy()
    recommendation_table_df['similarity'] = recommendation_table[0]
    rec_result = recommendation_table_df.sort_values(
        by='similarity', ascending=False).head(k)

    return rec_result


def parse_cookie(cookie, type=None):
    if cookie:
        cookie = cookie.split(",")
    else:
        cookie = []
    if type:
        cookie = [type(c) for c in cookie]
    return cookie
