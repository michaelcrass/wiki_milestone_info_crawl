import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_article_creation_time(wiki_url, article_title):
    try:
        article_url = f"{wiki_url}{article_title}"
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        history_link = soup.find("li", id="ca-history")
        if history_link:
            history_url = wiki_url + history_link.find("a")["href"]
            if "https://www.maintal.wiki/wiki//w" in history_url: #replace with your wiki's URL
                history_url = history_url.replace("https://www.maintal.wiki/wiki//w/", "https://www.maintal.wiki/w/")

            history_response = requests.get(history_url)
            history_response.raise_for_status()
            history_soup = BeautifulSoup(history_response.content, "html.parser")

            first_history_entry = history_soup.find("li", class_="mw-history-item")
            if first_history_entry:
                timestamp_element = first_history_entry.find("a", class_="mw-changeslist-date")
                if timestamp_element:
                    timestamp_text = timestamp_element.text.strip()
                    formats = ["%d %B %Y at %H:%M", "%Y-%m-%d %H:%M:%S", "%B %d, %Y, %H:%M %p", "%Y-%m-%dT%H:%M:%SZ"]
                    for fmt in formats:
                        try:
                            creation_time = datetime.strptime(timestamp_text, fmt)
                            return creation_time
                        except ValueError:
                            pass
                    print(f"Warning: Could not parse date format: {timestamp_text} for {article_title}")
                    return None
        print(f"Warning: History link not found for article {article_title}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {article_url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def find_100th_article_creation(wiki_url, start_page="Hauptseite"): #start_page can be changed. (or Main_Page)
    article_creation_times = {}
    article_count = 0
    next_page = start_page

    while True:
        try:
            page_url = f"{wiki_url}{next_page}"
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            creation_time = get_article_creation_time(wiki_url, next_page)
            if creation_time:
                article_creation_times[next_page] = creation_time
                article_count += 1

            if article_count >= 100:
                sorted_creation_times = sorted(article_creation_times.values())
                return sorted_creation_times[99] # 100th article

            # Find the next page link (this depends on your wiki's structure)
            next_link = soup.find("a", string=re.compile(r"next page", re.IGNORECASE)) #you may need to change this
            if not next_link:
                next_link = soup.find("a", string=re.compile(r"Next page", re.IGNORECASE)) #try other variations
            if not next_link:
                next_link = soup.find("a", string=re.compile(r"weiter", re.IGNORECASE)) #german next page.

            if next_link:
                next_page = next_link["href"].split("/wiki/")[-1] #get the page title from the link.
            else:
                break # No more pages

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {page_url}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    return None # If less than 100 articles were found

# Example usage:

wiki_base_url = "https://yourwiki.example.com/wiki/" # Replace with your wiki's URL
wiki_base_url = "https://www.maintal.wiki/wiki/"

creation_date_100th = find_100th_article_creation(wiki_base_url)

if creation_date_100th:
    print(f"The 100th article was created on: {creation_date_100th}")
else:
    print("Could not determine the 100th article creation date.")

