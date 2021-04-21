import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_prof_url(name):
    # magic number: 298 is the school id for cornell university in ratemyprofs
    formatted_name = name.replace(" ", "+")
    url = (
        "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Cornell+University&schoolID=298&query="
        + formatted_name
    )

    page = requests.get(url=url, headers=headers)
    pageData = page.text
    pageDataTemp = re.findall(r"ShowRatings\.jsp\?tid=\d+", pageData)

    results_len = len(pageDataTemp)
    if results_len == 0:
        return 404
    elif results_len == 1:
        pageDataFinal = "https://www.ratemyprofessors.com/" + pageDataTemp[0]
        return pageDataFinal
    else:
        return url


def get_rating(url):
    em = requests.get(url)
    content = em.content

    soup = BeautifulSoup(content, "html.parser")

    numerator = soup.find(
        "div", attrs={"class": "RatingValue__Numerator-qw8sqy-2 liyUjw"}
    ).text
    denominator = soup.find(
        "div", attrs={"class": "RatingValue__Denominator-qw8sqy-4 UqFtE"}
    ).text

    return (numerator + denominator).replace(" ", "")


def main():
    result = get_prof_url("Michael Clarkson")
    rating = get_rating(result)
    # print(result)
    print(rating)


if __name__ == "__main__":
    main()
