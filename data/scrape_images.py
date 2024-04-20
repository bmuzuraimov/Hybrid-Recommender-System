import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def get_udemy_course_image(course_url):
    base_url = 'https://www.udemy.com'
    full_url = base_url + course_url

    try:
        response = requests.get(full_url, timeout=10)  # Added timeout for better error handling
        response.raise_for_status()  # Will raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Failed to get the image for {course_url} due to {e}")
        return course_url, None

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Use a more specific selector to reliably select the cover image
    image_tags = soup.find_all('img')
    if len(image_tags) > 2 and 'src' in image_tags[2].attrs:
        return course_url, image_tags[2]['src']
    else:
        print(f"No suitable image found for {course_url}")
        return course_url, None

def update_course_info(df):
    urls = df['course_url'].tolist()
    results = {}

    # Setting up ThreadPoolExecutor with a progress bar from tqdm
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Preparing list of futures
        futures = [executor.submit(get_udemy_course_image, url) for url in urls]
        # Wrapping concurrent.futures.as_completed(futures) with tqdm for real-time progress updates
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(urls), desc="Fetching Images", unit="image"):
            url, image_src = future.result()
            results[url] = image_src

    # Mapping results back to the DataFrame
    df['cover_url'] = df['course_url'].map(results)
    return df

# Load course information
course_info = pd.read_pickle('./processed/course_info.pkl')

# Update course info with cover URLs
try:
    updated_course_info = update_course_info(course_info)
    updated_course_info.to_pickle('./processed/course_info.pkl')
except Exception as e:
    print(f"An error occurred while processing: {e}")
    # Optionally, you can still save progress here, depending on your requirement
    course_info.to_pickle('./processed/course_info.pkl')
