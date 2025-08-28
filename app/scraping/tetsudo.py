import requests
from bs4 import BeautifulSoup

from .cache import cache

@cache()
def scrape_tetsudo_articles():
    url = "https://www.tetsudo.com/column"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the topics list
    topics_list = soup.find('ul', class_='topics-list')

    # Get the first 4 list items
    articles = topics_list.find_all('li', class_='clearfix')[:4]

    result = []

    for article in articles:
        # Extract title and link from the h3 anchor tag
        title_link_tag = article.find('h3').find('a')
        title = title_link_tag.get_text(strip=True)
        link = "https://www.tetsudo.com" + title_link_tag['href']

        # Extract image URL
        image_tag = article.find('figure', class_='topics-image').find('img')
        image_url = image_tag['src'].strip()

        # Extract summary
        summary_tag = article.find('p', class_='topics-summary')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        result.append({
            "title": title,
            "image": image_url,
            "summary": summary,
            "link": link
        })

    return result