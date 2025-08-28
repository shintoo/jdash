from .sorae import scrape_sorae_articles
from .yahoo import scrape_yahoo_articles
from .tetsudo import scrape_tetsudo_articles
from .wired import scrape_wired_articles

scrapers = [
  {"website": "tetsudo" , "function": scrape_tetsudo_articles},
  {"website": "sorae", "function": scrape_sorae_articles},
  #{"website": "yahoo", "function": scrape_yahoo_articles},
  {"website": "wired", "function": scrape_wired_articles}
]
