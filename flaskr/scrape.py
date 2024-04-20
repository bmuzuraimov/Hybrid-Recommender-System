from .tools.scrape_tool import *

from flask import (
    Blueprint, current_app
)

bp = Blueprint('scrape', __name__, url_prefix='/scrape')


# This function aims to re-scrape the cover of the courses. Do not run it without supervisor!!.
@bp.route('/', methods=('GET', 'POST'))
def index():
    courses = getOriginalItems()

    totalNum = len(courses)
    current = 0

    file = open(f"{current_app.root_path}/static/ml_data_lab2/course_info_new.csv", "a")
    titles = courses[0]
    category = titles.pop(2)
    titles.append("cover_url")
    titles.append(category)
    file.write(','.join(titles) + "\n")
    file.close()

    for course in courses[1:]:
        print(f"{(current / totalNum) * 100 : .2f} %")
        image_url = get_course_png(course[1])
        category = course.pop(2)
        if image_url is not None:
            course.append(image_url)
        else:
            course.append("")
        course.append(category)
        file = open(f"{current_app.root_path}/static/ml_data_lab2/course_info_new.csv", "a")
        file.write(','.join(course) + "\n")
        file.close()
        current += 1

    file.close()

    return "Complete!"



