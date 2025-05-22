from googleapiclient.discovery import build
import pandas as pd
import time
import re

# API Key Setup
api_key = 'AIzaSyCnP_gQNW9KR5JK4eSqlkZEzm3f-UB_xkg'
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to search videos for a query
def search_videos(query, max_results=50):
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results,
        regionCode='IN'
    )
    response = request.execute()
    return response['items']

# Function to fetch comments for a video
def get_comments(video_id, max_results=40):
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            clean_comment = preprocess_text(comment)
            comments.append(clean_comment)
    except Exception as e:
        pass  # skip errors
    return list(set(comments))  # remove duplicate comments

# Preprocessing function for text cleaning
def preprocess_text(text):
    text = str(text)
    text = re.sub(r'[\n\r\t]', ' ', text)  # remove newlines/tabs
    text = re.sub(r'[^\w\s.,!?-]', '', text)  # remove emojis/special characters (keep punctuation)
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    text = text.strip()  # strip leading/trailing spaces
    return text

# Define query
query = "Hyderabad real estate"
videos = search_videos(query, max_results=50)

# Collect video details with comments
video_data = []

for video in videos:
    video_id = video['id']['videoId']
    title = preprocess_text(video['snippet'].get('title', 'N/A'))
    description = preprocess_text(video['snippet'].get('description', 'N/A'))
    publish_time = video['snippet'].get('publishedAt', 'N/A')
    channel = preprocess_text(video['snippet'].get('channelTitle', 'N/A'))

    comments = get_comments(video_id)
    time.sleep(1)  # polite delay

    video_data.append({
        'Video ID': video_id,
        'Video Title': title,
        'Description': description,
        'Published At': publish_time,
        'Channel': channel,
        'Comments': ' || '.join(comments) if comments else 'No Comments'
    })

# Convert to DataFrame
df = pd.DataFrame(video_data)

# Final clean-up: replace empty strings or None with 'N/A'
df = df.fillna('N/A')

# Save to CSV (with safe path handling)
output_path = r'C:\Users\Medis\OneDrive\Documents\Desktop\real_estate_trend\scraping\data\hyderabad_real_estate_youtube_data_clean.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print("✅ Data collected, preprocessed, and saved as clean CSV!")