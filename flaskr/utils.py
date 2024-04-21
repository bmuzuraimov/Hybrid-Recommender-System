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


def get_courses_by_category(courses, user_category, user_subcategory, user_price_ranges, user_num_lectures_ranges, user_content_length_minutes_ranges):
    results = []
    category = get_categories()
    subcategory = get_sub_categories()
    price_ranges = get_price_ranges()
    num_lectures_ranges = get_num_lectures_ranges()
    content_length_minutes_ranges = get_content_length_minutes_ranges()

    if len(user_category) > 0:
        # Convert user category IDs to integers and create a mask for these categories
        category_mask = category['id'].isin([int(id) for id in user_category])
        subcategory_mask = subcategory['id'].isin(
            [int(id) for id in user_subcategory])
        price_ranges_mask = price_ranges['id'].isin(
            [int(id) for id in user_price_ranges])
        num_lectures_ranges_mask = num_lectures_ranges['id'].isin(
            [int(id) for id in user_num_lectures_ranges])
        content_length_minutes_ranges_mask = content_length_minutes_ranges['id'].isin(
            [int(id) for id in user_content_length_minutes_ranges])

        # Get the category similarity matrix
        category_similarity_matrix, subcategory_similarity_matrix = get_similarity_matrices()
        # Compute the average user category vector using the similarity matrix
        user_category_vector = np.nanmean(
            category_similarity_matrix[category_mask], axis=0)
        user_category_vector[np.isnan(user_category_vector)] = 0

        user_subcategory_vector = np.nanmean(
            subcategory_similarity_matrix[subcategory_mask], axis=0)
        user_subcategory_vector[np.isnan(user_subcategory_vector)] = 0
        # user_price_vector = np.mean(price_bin2vec[price_ranges_mask], axis=0)
        # user_num_lectures_vector = np.mean(num_lectures_bin2vec[num_lectures_ranges_mask], axis=0)
        # user_content_length_minutes_vector = np.mean(content_length_minutes_bin2vec[content_length_minutes_ranges_mask], axis=0)

        # Ensure each row in 'category_dist' is properly shaped as a numpy array
        user_preference_vector = np.concatenate(
            [user_category_vector, user_subcategory_vector, np.zeros(29)])
        courses['similarity'] = courses['profile'].apply(
            lambda x: np.dot(x, user_preference_vector))
        # Filter courses based on similarity score and select the top 30
        results = courses[courses['similarity'] > 0].nlargest(30, 'similarity')
    # Return the result as a list of dictionaries if results are found
    if len(results) > 0:
        return results.reset_index().to_dict('records')
    return results


def get_recommendation_by_content_based_filtering(courses, user_rates):
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

    recommended_courses = courses[courses['similarity'] > 0].nlargest(
        20, 'similarity')

    if not recommended_courses.empty:
        return recommended_courses.reset_index().to_dict('records'), "These courses are recommended based on your ratings."
    return [], "No recommendations."


def get_liked_similar_by(courses, user_likes):
    results = []

    if len(user_likes) > 0:
        # Assuming 'courses' is a DataFrame with 'profile' being a column of arrays or list
        user_profile = courses.loc[courses.index.isin(user_likes), 'profile'].mean(axis=0)
        course_rep_matrix = np.stack(courses['profile'].values)  # Stack arrays row-wise
        
        results = _generate_recommendation_results(user_profile, course_rep_matrix, courses, 12)
        
    if results and not results.empty:
        return results.reset_index().to_dict('records'), "The courses are similar to your liked courses."
    return [], "No similar courses found."

def _generate_recommendation_results(user_profile, item_rep_matrix, courses_data, k=12):
    # Ensure the user_profile is a 2D array with shape (1, number of features)
    user_profile_reshaped = user_profile.reshape(1, -1)
    # item_rep_matrix should already be in shape (number of courses, number of features)
    
    # Compute the cosine similarity
    recommendation_table = cosine_similarity(user_profile_reshaped, item_rep_matrix)
    
    # Convert similarity scores to a DataFrame column
    recommendation_table_df = courses_data.copy()
    recommendation_table_df['similarity'] = recommendation_table[0]
    rec_result = recommendation_table_df.sort_values(by='similarity', ascending=False).head(k)
    
    return rec_result


def parse_cookie(cookie, type=None):
    if cookie:
        cookie = cookie.split(",")
    else:
        cookie = []
    if type:
        cookie = [type(c) for c in cookie]
    return cookie
