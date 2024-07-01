import aiohttp
from bs4 import BeautifulSoup

recipe_prompt = """
You are RecipeExtractorGPT.
Your goal is to extract recipe content from text and return a JSON representation of the useful information.

The JSON should be structured like this:

```
{
  "title": "Scrambled eggs",
  "ingredients": {
    "eggs": "2",
    "butter": "1 tbsp",
    "milk": "1 tbsp",
    "salt": "1 pinch"
  },
  "directions": [
    "Beat eggs, milk, and salt together in a bowl until thoroughly combined.",
    "Heat butter in a large skillet over medium-high heat. Pour egg mixture into the hot skillet; cook and stir until eggs are set, 3 to 5 minutes."
  ],
  "servings": 2,
  "prep_time": 5,
  "cook_time": 5,
  "total_time": 10,
  "tags": [
    "breakfast",
    "eggs",
    "scrambled"
  ],
  "source": "https://recipes.com/scrambled-eggs/",
}
```

The user will provide text content from a web page.
It is not very well structured, but the recipe is in there.
Please look carefully for the useful information about the recipe.
IMPORTANT: Return the result as JSON in a Markdown code block surrounded with three backticks!
"""


async def scrape_page_with_url(url: str, max_length: int = 14000) -> str:
    """
    Given a URL, scrapes the web page and return the contents. This also adds adds the
    URL to the beginning of the text.

    Parameters
    ----------
    url:
      The URL to scrape
    max_length:
      Max length of recipe text to process. This is to prevent the model from running
      out of tokens. 14000 bytes translates to approximately 3200 tokens.
    """
    contents = await scrape_page(url)
    # Trim the string so that the prompt and reply will fit in the token limit.. It
    # would be better to trim by tokens, but that requires using the tiktoken package,
    # which can be very slow to load when running on containerized servers, because it
    # needs to download the model from the internet each time the container starts.
    contents = contents[:max_length]
    return f"From: {url}\n\n" + contents


async def scrape_page(url: str) -> str:
    # Asynchronously send an HTTP request to the URL.
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise aiohttp.ClientError(f"An error occurred: {response.status}")
            html = await response.text()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # List of element IDs or class names to remove
    elements_to_remove = [
        "header",
        "footer",
        "sidebar",
        "nav",
        "menu",
        "ad",
        "advertisement",
        "cookie-banner",
        "popup",
        "social",
        "breadcrumb",
        "pagination",
        "comment",
        "comments",
    ]

    # Remove unwanted elements by ID or class name
    for element in elements_to_remove:
        for e in soup.find_all(id=element) + soup.find_all(class_=element):
            e.decompose()

    # Extract text from the remaining HTML tags
    text = " ".join(soup.stripped_strings)

    return text
