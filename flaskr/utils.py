import pandas as pd
from .tools.data_tool import (
    ratesFromUser,
    getCategories,
    getSubCategories,
    getPriceRanges,
    getNumLecturesRanges,
    getContentLengthMinutesRanges,
    get_category_similarity_matrix,
    get_subcategory_similarity_matrix,
    get_price_bin2vec,
    get_num_lectures_bin2vec,
    get_content_length_minutes_bin2vec
)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

rootPath = os.path.abspath(os.getcwd())


def get_user_likes_by(courses, user_likes):
    results = []

    if len(user_likes) > 0:
        mask = courses['id'].isin([int(courseId) for courseId in user_likes])
        results = courses.loc[mask]

        original_orders = pd.DataFrame()
        for _id in user_likes:
            course = results.loc[results['id'] == int(_id)]
            if len(original_orders) == 0:
                original_orders = course
            else:
                original_orders = pd.concat([course, original_orders])
        results = original_orders

    # return the result
    if len(results) > 0:
        return results.to_dict('records')
    return results


def get_courses_by_category(courses, user_category, user_subcategory, user_price_ranges, user_num_lectures_ranges, user_content_length_minutes_ranges):
    results = []
    category = getCategories()
    subcategory = getSubCategories()
    price_ranges = getPriceRanges()
    num_lectures_ranges = getNumLecturesRanges()
    content_length_minutes_ranges = getContentLengthMinutesRanges()

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
        category_similarity_matrix = get_category_similarity_matrix()
        subcategory_similarity_matrix = get_subcategory_similarity_matrix()
        price_bin2vec = get_price_bin2vec()
        num_lectures_bin2vec = get_num_lectures_bin2vec()
        content_length_minutes_bin2vec = get_content_length_minutes_bin2vec()

        # Compute the average user category vector using the similarity matrix
        user_category_vector = np.mean(
            category_similarity_matrix[category_mask], axis=0)
        user_subcategory_vector = np.mean(
            subcategory_similarity_matrix[subcategory_mask], axis=0)
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
        return results.to_dict('records')
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
        return recommended_courses.to_dict('records'), "These courses are recommended based on your ratings."
    return [], "No recommendations."


# Modify this function
def get_liked_similar_by(courses, user_likes):
    results = []

    # ==== Do some operations ====
    if len(user_likes) > 0:

        # # Step 1: Representing items with one-hot vectors
        item_rep_matrix, item_rep_vector, feature_list = item_representation_based_course_category(
            courses)

        # # Step 2: Building user profile
        user_profile = build_user_profile(
            user_likes, item_rep_vector, feature_list)

        # # Step 3: Predicting user interest in items
        results = generate_recommendation_results(
            user_profile, item_rep_matrix, item_rep_vector, 12)
        # course_TF_IDF_vector, tfidf_feature_list = build_tfidf_vectors()
        # user_profile = build_tfidf_user_profile(user_likes, course_TF_IDF_vector, tfidf_feature_list)
        # results = generate_tf_idf_recommendation_results(user_profile, course_TF_IDF_vector, tfidf_feature_list, 12)
    # Return the result
    if len(results) > 0:
        return results.to_dict('records'), "The courses are similar to your liked courses."
    return results, "No similar courses found."

    # ==== End ====


def item_representation_based_course_category(courses_df):
    courses_with_category = courses_df.copy(deep=True)

    genre_list = courses_with_category.columns[5:]
    courses_genre_matrix = courses_with_category[genre_list].to_numpy()
    return courses_genre_matrix, courses_with_category, genre_list


def build_user_profile(courseIds, item_rep_vector, feature_list, normalized=True):

    # Calculate item representation matrix to represent user profiles
    user_course_rating_df = item_rep_vector[item_rep_vector['id'].isin(
        courseIds)]
    user_course_df = user_course_rating_df[feature_list].mean()
    user_profile = user_course_df.T

    if normalized:
        user_profile = user_profile / sum(user_profile.values)

    return user_profile


def generate_recommendation_results(user_profile, item_rep_matrix, courses_data, k=12):

    u_v = user_profile.values
    u_v_matrix = [u_v]

    # Comput the cosine similarity
    recommendation_table = cosine_similarity(u_v_matrix, item_rep_matrix)

    recommendation_table_df = courses_data.copy(deep=True)
    recommendation_table_df['similarity'] = recommendation_table[0]
    rec_result = recommendation_table_df.sort_values(
        by=['similarity'], ascending=False)[:k]

    return rec_result


def parse_cookie(cookie, type=None):
    if cookie:
        cookie = cookie.split(",")
    else:
        cookie = []
    if type:
        cookie = [type(c) for c in cookie]
    return cookie
