import requests
from bs4 import BeautifulSoup
import csv
import time
from newspaper import Article
import re
import os

# Correct base URL for pagination
base_url = "https://regnews.in/category/latest-updates"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Define Hyderabad areas
HYD_AREAS = [
    "telangana", "Hyderabad", "Secunderabad", "Hitec City", "Gachibowli", "Madhapur", "Kukatpally", "Ameerpet",
    "Dilsukhnagar", "Miyapur", "LB Nagar", "Uppal", "Kompally", "Mehdipatnam", "Charminar", "Nampally",
    "Begumpet", "Banjara Hills", "Jubilee Hills", "Kondapur", "Shamshabad", "Attapur", "Chandanagar",
    "Manikonda", "Nagole", "Khairatabad", "Moosapet", "Serilingampally", "Adibatla", "Tellapur", "Narsingi",
    "Shamirpet", "Financial District", "Khajaguda", "Patancheru", "Boduppal", "Rampally", "Yapral",
    "Keesara", "Pocharam", "Bachupally", "Alkapuri", "Pedda Amberpet", "Hayathnagar"
]

# Define real estate related keywords
REAL_ESTATE_KEYWORDS = [
    "real estate", "property", "plot", "villa", "flat", "apartment", "housing", "home", "2BHK", "3BHK",
    "independent house", "duplex", "layout", "project", "residential", "commercial", "township",
    "investment", "buy", "sell", "lease", "rent", "registration", "sale deed", "development",
    "construction", "builder", "developer", "infrastructure", "approval", "permissions", "RERA", "TS-bPASS",
    "urban planning", "greenfield", "brownfield", "zoning", "SEZ", "IT park", "pharma city",
    "startup hub", "tech park", "data center", "logistics hub", "smart city", "HMDA", "GHMC", "master plan",
    "ring road", "metro rail", "MMTS", "collectorate", "land acquisition", "land pooling", "regularization",
    "price hike", "land rate", "demand", "launch", "occupancy", "inventory", "handover",
    "luxury", "premium", "gated community", "affordable housing", "connectivity", "flyover", "bypass road"
]

# Check if text contains any keyword from list
def contains_any(text, keywords):
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

# Article is relevant if it contains BOTH an area and a real estate keyword
def is_relevant_article(text):
    return contains_any(text, HYD_AREAS) and contains_any(text, REAL_ESTATE_KEYWORDS)

# Preprocess article text (clean whitespace, newlines, etc.)
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces/newlines
    text = text.strip()
    return text

# Get full article text from URL
def get_full_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return clean_text(article.text)
    except Exception as e:
        print(f"❌ Failed to fetch full text from {url}: {e}")
        return "N/A"

# Extract all articles from a given page
def extract_articles(page_url):
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []

    post_blocks = soup.select("div.td-module-container")
    if not post_blocks:
        print(f"⚠️ No articles found at: {page_url}")
        return []

    for block in post_blocks:
        try:
            title_tag = block.select_one("h3.entry-title a")
            if not title_tag:
                continue
            title = clean_text(title_tag.get_text())
            link = title_tag["href"]

            date_tag = block.select_one("time.entry-date")
            date = clean_text(date_tag.get_text()) if date_tag else "N/A"

            summary_tag = block.select_one("div.td-excerpt")
            summary = clean_text(summary_tag.get_text()) if summary_tag else "N/A"

            full_text = get_full_article_text(link)

            combined_text = f"{title} {summary} {full_text}"
            if is_relevant_article(combined_text):
                articles.append({
                    "Title": title,
                    "Link": link,
                    "Date": date,
                    "Summary": summary,
                    "Full_Article_Text": full_text
                })
                print(f"✅ Collected: {title}")
            else:
                print(f"⏩ Skipped (Not Hyderabad + real estate): {title}")

            time.sleep(1)

        except Exception as e:
            print(f"❌ Error parsing article block: {e}")
    
    return articles

# Loop through N pages
def scrape_regnews(pages=5):
    all_articles = []
    for page in range(1, pages + 1):
        print(f"\n🔎 Scraping page {page}...")
        page_url = f"{base_url}/page/{page}/" if page > 1 else base_url
        all_articles.extend(extract_articles(page_url))
        time.sleep(2)
    return all_articles

# Save articles to CSV at given path
def save_to_csv(data, filepath):
    if not data:
        print("❌ No data to save.")
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    keys = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ Saved {len(data)} Hyderabad real estate articles to: {filepath}")

# Run the full scraper
if __name__ == "__main__":
    output_path = r"C:\Users\Medis\OneDrive\Documents\Desktop\real_estate_trend\scraping\data\hyderabad_regnews_articles.csv"
    articles = scrape_regnews(pages=5)
    save_to_csv(articles, output_path)
