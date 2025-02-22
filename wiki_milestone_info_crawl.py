import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import datetime
import configparser

# Base URL of your wiki (change accordingly)

# read config
config = configparser.ConfigParser()
try:
    config.read('config.ini')
except ValueError as e:
    print(f"Fehler: {e}")
    input("..")
WIKI_BASE_URL = config['wiki']['url'] 
print(WIKI_BASE_URL)

# WIKI_BASE_URL = "https://www.mywiki.com/w"
# or config.ini:
# [wiki]
# url= https://www.mywiki.com/w

WIKI_API_URL = f"{WIKI_BASE_URL}/api.php"

# Function to get all article titles
def get_all_articles():
    articles = []
    cont = None
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "max",
            "format": "json"
        }
        if cont:
            params.update(cont)
        
        response = requests.get(WIKI_API_URL, params=params).json()
        articles.extend([page["title"] for page in response["query"]["allpages"]])
        cont = response.get("continue")
        if not cont:
            break
    
    return articles

# Function to get the creation date of an article
def get_creation_date(title):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvlimit": 1,
        "rvprop": "timestamp",
        "rvdir": "newer",
        "titles": title,
        "format": "json"
    }
    response = requests.get(WIKI_API_URL, params=params).json()
    pages = response.get("query", {}).get("pages", {})
    for page in pages.values():
        if "revisions" in page:
            return page["revisions"][0]["timestamp"]
    return None

# Main function to determine when the wiki reached 100 articles
def find_article_number(number):
    articles = get_all_articles()
    creation_data = []
    
    for title in articles:
        print(title)
        date = get_creation_date(title)
        if date:
            creation_data.append((title, datetime.datetime.fromisoformat(date.replace("Z", ""))))
    
    creation_data.sort(key=lambda x: x[1])
    if len(creation_data) >= number:
        return creation_data[number - 1][1].date(), creation_data[number - 1][0], len(articles)
    else:
        return f"Wiki does not have {number} articles yet.", None, None

# Run the script
if __name__ == "__main__":
    number = 150
    date, title, anzahl_artikel = find_article_number(number)
    print(f"Date when article number {number} was created:", date)
    print(f"Title of the article number {number}:", title)