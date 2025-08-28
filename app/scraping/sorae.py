import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .cache import cache

@cache()
def scrape_sorae_articles():
    """
    Scrapes the sorae.info homepage for the first 4 articles.

    Returns:
        list: A list of dictionaries containing article data.
    """
    base_url = "https://sorae.info/astronomy"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    articles_section = soup.find('section', class_='wrap-post-box')

    if not articles_section:
        print("Could not find the articles section.")
        return []

    articles_data = []
    # Find direct child <article> elements
    articles = articles_section.find_all('article', recursive=False)

    for article in articles[:4]: # Limit to first 4 articles
        # --- Find Link and Title ---
        # The link and title are inside the div with data-href and the <a> tag within .post-title
        container_div = article.find('div', class_='post-box-contents')
        link = container_div.get('data-href') if container_div else None
        if link:
            link = link.strip() # Remove potential trailing spaces

        title_a_tag = article.find('div', class_='post-title').find('a') if article.find('div', class_='post-title') else None
        title = title_a_tag.get('title') if title_a_tag and title_a_tag.get('title') else (title_a_tag.get_text(strip=True) if title_a_tag else None)
        # If link wasn't found via data-href, try getting it from the title link
        if not link and title_a_tag and title_a_tag.get('href'):
             link = urljoin(base_url, title_a_tag.get('href').strip())


        # --- Find Image URL ---
        img_tag = article.find('figure', class_='post_thumbnail').find('img') if article.find('figure', class_='post_thumbnail') else None
        image_url = None
        if img_tag:
            # Prefer 'src' attribute, fallback to 'data-src' if 'src' is not a link
            image_url = img_tag.get('src')

            if "data:image" in image_url:
                image_url = img_tag.get('data-src')

            if image_url:
                 image_url = image_url.strip()

        # --- Find Summary ---
        summary_div = article.find('div', class_='post-substr')
        summary = summary_div.get_text(strip=True) if summary_div else None

        # Add to list if we have at least a title or link
        if title or link:
            # Use the link found via data-href or constructed from href
            final_link = link if link else (title_a_tag.get('href').strip() if title_a_tag else None)


            articles_data.append({
                "title": title,
                "image": image_url,
                "summary": summary,
                "link": final_link
            })

    return articles_data

# Example usage:
if __name__ == "__main__":
    articles = scrape_sorae_articles()
    for article in articles:
        print(article)