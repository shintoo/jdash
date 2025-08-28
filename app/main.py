from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from typing import Dict
import asyncio

from scraping import scrapers

app = FastAPI(title="News Article Scraper API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Set to True if your frontend needs to send cookies or authorization headers
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/ping")
async def ping():
    return {"pong": "News Article Scraper API is running"}

@app.get("/articles")
async def get_articles() -> Dict:
    """
    Retrieve the latest articles from all configured news and blog sites.
    Returns a compiled list of articles grouped by website.
    """

    # Execute all scraping functions concurrently
    results = await asyncio.gather(
        *[run_scraper(scraper["function"]) for scraper in scrapers],
        return_exceptions=True
    )

    # Filter out any exceptions and format successful results
    formatted_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Handle scraping errors gracefully
            formatted_results.append({
                "website": scrapers[i]["website"],
                "articles": {"articles": []},
                "error": str(result)
            })
        else:
            formatted_results.append({
                "website": scrapers[i]["website"],
                "articles": result
            })

    return {"results": formatted_results}

async def run_scraper(scraper_function) -> Dict:
    """
    Run a scraper function and return its results.
    This helper function allows us to run synchronous scraping functions
    in a way that's compatible with async/await.
    """
    loop = asyncio.get_event_loop()

    result = await loop.run_in_executor(None, scraper_function)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)