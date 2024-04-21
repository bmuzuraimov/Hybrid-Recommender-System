import os
import pandas as pd
import pickle
import numpy as np

BASE_PATH = os.path.abspath(os.getcwd())


def load_data():
    """Load all necessary data for application initialization."""
    return (get_courses(), get_categories(), get_sub_categories(), get_price_ranges(),
            get_num_lectures_ranges(), get_content_length_minutes_ranges())


def get_courses():
    """Fetch and randomize course information from a pickle file."""
    path = f"{BASE_PATH}/data/processed/course_info_minified.pkl"
    courses_df = pd.read_pickle(path)
    return courses_df.sample(frac=1).reset_index(drop=True).set_index('id')


def get_categories():
    path = f"{BASE_PATH}/data/processed/category.pkl"
    with open(path, 'rb') as f:
        categories = pickle.load(f)
    categories_df = pd.DataFrame(categories)
    categories_df.set_index('id')
    return categories_df


def get_sub_categories():
    path = f"{BASE_PATH}/data/processed/subcategory.pkl"
    with open(path, 'rb') as f:
        subcategories = pickle.load(f)
    subcategories_df = pd.DataFrame(subcategories)
    subcategories_df.set_index('id')
    return subcategories_df


def get_price_ranges():
    path = f"{BASE_PATH}/data/processed/id2price.pkl"
    with open(path, 'rb') as f:
        price = pickle.load(f)
    price_df = pd.DataFrame(price)
    price_df.set_index('id')
    return price_df


def get_num_lectures_ranges():
    path = f"{BASE_PATH}/data/processed/id2num_lectures.pkl"
    with open(path, 'rb') as f:
        num_lectures = pickle.load(f)
    num_lectures_df = pd.DataFrame(num_lectures)
    num_lectures_df.set_index('id')
    return num_lectures_df


def get_content_length_minutes_ranges():
    path = f"{BASE_PATH}/data/processed/id2content_length_min.pkl"
    with open(path, 'rb') as f:
        content_length_min = pickle.load(f)
    content_length_min_df = pd.DataFrame(content_length_min)
    content_length_min_df.set_index('id')
    return content_length_min_df


def get_similarity_matrices():
    """Load all similarity matrices for categories and subcategories."""
    category_matrix_path = f"{BASE_PATH}/data/processed/category_similarity_matrix.npy"
    subcategory_matrix_path = f"{BASE_PATH}/data/processed/subcategory_similarity_matrix.npy"
    category_similarity_matrix = np.load(category_matrix_path)
    subcategory_similarity_matrix = np.load(subcategory_matrix_path)
    return category_similarity_matrix, subcategory_similarity_matrix


def get_bin2vec_mappings():
    """Load all binary vector mappings for price, number of lectures, and content length."""
    price_path = f"{BASE_PATH}/data/processed/bins2price.pkl"
    num_lectures_path = f"{BASE_PATH}/data/processed/bins2num_lectures.pkl"
    content_length_path = f"{BASE_PATH}/data/processed/bins2content_length_min.pkl"
    with open(price_path, 'rb') as file:
        price_bin2vec = pickle.load(file)
    with open(num_lectures_path, 'rb') as file:
        num_lectures_bin2vec = pickle.load(file)
    with open(content_length_path, 'rb') as file:
        content_length_minutes_bin2vec = pickle.load(file)
    return price_bin2vec, num_lectures_bin2vec, content_length_minutes_bin2vec

# user id | item id | rating | timestamp
def getRates():
    path = f"{BASE_PATH()}/data/processed/ratings.csv"
    df = pd.read_csv(path, delimiter=",", names=[
                     "userId", "courseId", "rating", "timestamp"])
    df = df.drop(columns='timestamp')
    df = df[['userId', 'courseId', 'rating']]

    return df

# itemID | userID | rating
def ratesFromUser(rates):
    itemID = []
    userID = []
    rating = []

    for rate in rates:
        items = rate.split("|")
        userID.append(int(items[0]))
        itemID.append(int(items[1]))
        rating.append(int(items[2]))

    ratings_dict = {
        "userId": userID,
        "id": itemID,
        "rating": rating,
    }

    return pd.DataFrame(ratings_dict)


