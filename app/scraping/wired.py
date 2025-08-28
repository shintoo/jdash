import requests
from bs4 import BeautifulSoup

from .cache import cache

@cache()
def scrape_wired_articles():
    url = "https://wired.jp/science"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the container with articles
    container = soup.find("div", class_="SummaryCollectionGridItems-TvFTI")
    if not container:
        return []

    # Get the first four article divs inside the container
    articles = container.find_all("div", class_="summary-item", recursive=False)[:4]

    results = []

    for article in articles:
        # Title
        title_tag = article.find("h2", class_="summary-item__hed")
        title = title_tag.get_text(strip=True) if title_tag else "No title"

        # Link
        link_tag = article.find("a", class_="summary-item__hed-link")
        link = "https://wired.jp" + link_tag["href"] if link_tag and link_tag.get("href") else "#"

        # Image URL
        img_tag = article.find("img", class_="responsive-image__image")
        img_url = img_tag["src"] if img_tag and img_tag.get("src") else "No image"

        # Summary
        summary_tag = article.find("div", class_="summary-item__dek")
        summary = summary_tag.get_text(strip=True) if summary_tag else "No summary"

        results.append({
            "title": title,
            "link": link,
            "image": img_url,
            "summary": summary
        })

    return results
