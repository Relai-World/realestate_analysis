# Realestate Analysis

---

## Hyderabad Real Estate YouTube Comments Scraper

### Project Description

This Python script collects YouTube video metadata and comments related to **Hyderabad real estate** using the YouTube Data API v3. It searches for videos matching a specific query, extracts video details, fetches top-level comments, cleans and preprocesses the textual data, and saves the compiled dataset as a CSV file.

The resulting dataset can be used for sentiment analysis, market research, and other downstream real estate analytics focused on Hyderabad.

### Features

- Search YouTube videos by keyword with region filtering (`regionCode='IN'`).
- Fetch video metadata including video ID, title, description, publication date, and channel name.
- Extract and preprocess top-level comments for each video, including removal of special characters, emojis, and redundant whitespace.
- Deduplicate comments to avoid redundancy.
- Save the cleaned and aggregated data in a structured CSV format for easy analysis.

### Requirements

- Python 3.7 or higher
- Google API Client Library for Python
- Pandas

### Installation

1. Clone the repository or download the script.

2. Install dependencies via pip:

   ```bash
   pip install google-api-python-client pandas
Setup Instructions
Obtain YouTube Data API Key:

Visit Google Cloud Console.

Create or select a project.

Enable the YouTube Data API v3.

Generate an API key.

Replace the api_key variable in the script with your API key string.

Modify Output Path:

Adjust the output_path variable to point to your desired CSV save location.

Usage
Run the script directly:

bash
Copy
Edit
python youtube_scraper.py
The script will:

Search YouTube for videos matching the query "Hyderabad real estate".

For each video, collect metadata and fetch up to 40 top-level comments.

Preprocess and clean the comments.

Save the compiled data as a CSV file at the specified location.

Hyderabad Real Estate Twitter Sentiment & Suitability Analysis
Project Overview
This Python script collects recent tweets related to Hyderabad real estate using the Twitter API v2, analyzes their sentiment, and categorizes them by locality, suitability (residential, commercial, industrial), and reasons cited (infrastructure, pricing, amenities, growth). It produces both a detailed tweet-level dataset and an aggregated summary with area-wise insights.

This tool provides data-driven insights on public opinion about Hyderabad’s real estate market by extracting meaningful patterns from Twitter discussions.

Features
Connects to Twitter API v2 via Bearer Token authentication.

Fetches recent tweets matching real estate-related queries in Hyderabad.

Cleans and preprocesses tweets by removing URLs, mentions, hashtags, and special characters.

Performs sentiment analysis using TextBlob to classify tweets as positive, neutral, or negative.

Extracts Hyderabad localities mentioned in tweets from a predefined list.

Categorizes tweets by suitability and reasons based on keyword matching.

Aggregates statistics per locality including sentiment distribution, primary suitability, and top reasons.

Outputs summary and detailed tweet data as CSV files.

Requirements
Python 3.7+

Tweepy

TextBlob

Pandas

NLTK (for TextBlob dependencies)

Installation
Clone the repository or download the script.

Install required packages:

bash
Copy
Edit
pip install tweepy textblob pandas nltk
(Optional) If running TextBlob for the first time, download necessary NLTK corpora:

python
Copy
Edit
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
Configuration
Bearer Token: Obtain from Twitter Developer Portal and set it in the CONFIG dictionary inside the script.

Tweet Count: Adjust the number of tweets to fetch (tweet_count in CONFIG).

CSV Export: Toggle CSV export and specify filenames in the CONFIG dictionary.

Localities: The script uses a predefined list of Hyderabad localities to detect areas mentioned in tweets.

Keywords: Suitability and reasons are matched from defined keyword lists in the script.

Usage
Run the script:

bash
Copy
Edit
python twitter_hyderabad_real_estate_analysis.py
The script will:

Authenticate with Twitter API.

Fetch recent tweets related to Hyderabad real estate (excluding retweets and non-English tweets).

Analyze sentiment, locations, suitability, and reasons.

Print an area-wise summary to the console.

Save detailed tweet data and summary statistics as CSV files if enabled.

Hyderabad Real Estate News Scraper (regnews.in)
This Python script scrapes the latest real estate-related news articles focused on Hyderabad and surrounding areas from regnews.in. It extracts article metadata such as title, link, date, summary, and the full article text, saving the scraped data as a CSV file.

Features
Scrapes multiple pages of latest updates from regnews.in.

Filters articles based on relevance to Hyderabad localities and real estate keywords.

Extracts article title, link, publication date, summary, and full article content.

Uses the newspaper3k library for full article extraction.

Saves results to a CSV file with UTF-8 encoding.

Handles pagination and rate limiting with delays.

Includes user-agent headers to mimic browser requests.

Requirements
Python 3.7 or higher

requests

beautifulsoup4

newspaper3k

lxml (optional but recommended)

Installation
bash
Copy
Edit
pip install requests beautifulsoup4 newspaper3k lxml
Usage
Clone or download the script.

Modify the output_path variable in the script to your desired CSV output location.

Run the script:

bash
Copy
Edit
python scraper.py
Instagram Hyderabad Real Estate Area Mentions Scraper
This script fetches recent Instagram posts and comments from a specified Instagram Business Account using the Instagram Graph API, extracting mentions of predefined Hyderabad localities related to real estate discussions.

Features
Connects to Instagram Graph API to fetch posts and comments.

Extracts mentions of Hyderabad localities from captions and comments.

Supports fetching up to 60 recent posts and 50 comments per post.

Saves combined post and comment data in a structured CSV file.

Requirements
Python 3.7 or higher

requests

Installation
bash
Copy
Edit
pip install requests
Setup
Obtain Instagram Graph API access token and Business Account ID.

Update ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID variables in the script.

Configure HYD_AREAS list for localities.

Set DATA_FOLDER for CSV output.

Usage
bash
Copy
Edit
python instagram_hyd_area_mentions.py
Hyderabad Real Estate Reddit Scraper
This Python script scrapes Reddit posts and comments from selected subreddits to identify discussions related to real estate and Hyderabad localities. It filters content mentioning real estate keywords and area names, saving relevant data into a CSV file.

Features
Connects to Reddit using the praw API wrapper.

Scrapes posts and comments from multiple subreddits.

Filters content by keywords and localities.

Saves filtered data to CSV.

Requirements
Python 3.7 or higher

praw

pandas

Installation
bash
Copy
Edit
pip install praw pandas
Setup
Create a Reddit App and obtain client_id, client_secret, and set user_agent.

Update credentials in the script.

Customize keywords, areas, and subreddits as needed.

Usage
bash
Copy
Edit
python reddit_realestate_scraper.py
Hyderabad Real Estate Analysis with Perplexity AI
This project leverages the Perplexity AI API to gather and analyze real estate information across 70+ Hyderabad localities. It scrapes detailed area-wise data about projects, government infrastructure, facilities, connectivity, risks, and gaps, performs sentiment analysis, and visualizes results in a Streamlit app.

Features
Automated data extraction with curated prompts.

Sentiment analysis classifying Positive, Negative, Neutral per area.

Interactive Streamlit dashboard showing:

Government developments per area

Facilities and gaps

Connectivity and challenges

Areas with least facilities/connectivity

Chatbot interface for queries

Saves data with timestamps in CSV files.

Project Structure
bash
Copy
Edit
scraping/
├── data/
│   └── real_estate_perplexity_data_YYYYMMDD_HHMM.csv
main.py                 # Data extraction and Streamlit app
requirements.txt        # Python dependencies
README.md               # This documentation
Prerequisites
Python 3.8+

Perplexity AI API key (https://www.perplexity.ai/)

Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/hyderabad-real-estate-analysis.git
cd hyderabad-real-estate-analysis
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set your Perplexity API key as an environment variable or update it directly in the script:

bash
Copy
Edit
export PERPLEXITY_API_KEY="your_api_key_here"
Running the Data Extraction
bash
Copy
Edit
python main.py
This fetches data for all predefined areas asynchronously from Perplexity AI and saves the output CSV in scraping/data with a timestamp.

Running the Streamlit App
Start the interactive dashboard:

bash
Copy
Edit
streamlit run main.py
Open the displayed URL (usually http://localhost:8501) in your browser to explore real estate insights and chat with the data-driven assistant.
