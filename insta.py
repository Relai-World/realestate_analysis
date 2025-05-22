import requests
import csv
import os
from datetime import datetime

# Replace with your actual access token and business account ID
ACCESS_TOKEN = 'EAAQrWCb5OZCwBOzfQZAZBVkeZAO018UFemJCOLx6aXEzzJbJxMJj90eSw6XoPPx3qdWeu2D71OYWIBm16FZCsTsqXeXmI3WUHO4wcYHYqjJ4zkIAB6OUwa3zxgXDqZBBJ1XCbeXu3MYsrP8McWTwRFLtrTI6VpZCaGTJO6VpJKnkoIZCQjNnH4Gk'
INSTAGRAM_ACCOUNT_ID = '17841473977672663'

# Folder to save CSV
DATA_FOLDER = r"C:\Users\Medis\OneDrive\Documents\Desktop\real_estate_trend\scraping\data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# List of Hyderabad areas you want to track mentions for
HYD_AREAS = [
    'gachibowli', 'hitech city', 'madhapur', 'kondapur', 'manikonda',
    'jubilee hills', 'banjara hills', 'kokapet', 'financial district',
    'shamshabad', 'kompally', 'uppal', 'lb nagar', 'adilabad',
    'kukatpally', 'bowenpally', 'narsingi', 'tellapur', 'patancheru'
]

# Fetch latest posts (up to 60)
def fetch_posts(limit=60):
    posts = []
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        'fields': 'id,caption,timestamp,media_url,permalink',
        'limit': 25,
        'access_token': ACCESS_TOKEN
    }
    while url and len(posts) < limit:
        response = requests.get(url, params=params).json()
        posts.extend(response.get('data', []))
        paging = response.get('paging', {})
        url = paging.get('next')
        params = None
        if len(posts) >= limit:
            break
    return posts[:limit]

# Fetch comments for a post (up to 50)
def fetch_comments(post_id, limit=50):
    comments = []
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
    params = {
        'fields': 'id,text,timestamp,username',
        'limit': 25,
        'access_token': ACCESS_TOKEN
    }
    while url and len(comments) < limit:
        response = requests.get(url, params=params).json()
        comments.extend(response.get('data', []))
        paging = response.get('paging', {})
        url = paging.get('next')
        params = None
        if len(comments) >= limit:
            break
    return comments[:limit]

# Check for Hyderabad area mentions in a text
def extract_area(text):
    if text:
        text_lower = text.lower()
        for area in HYD_AREAS:
            if area in text_lower:
                return area.title()  # Return with capitalized format
    return ''

# Save posts and comments mentioning specific areas into one file
def save_data_combined(posts):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    combined_file = os.path.join(DATA_FOLDER, f"instagram_hyd_area_mentions_{timestamp}.csv")

    with open(combined_file, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'type', 'post_id', 'caption', 'post_timestamp', 'media_url', 'permalink',
            'comment_id', 'username', 'comment_text', 'comment_timestamp', 'area_mentioned'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        relevant_post_count = 0
        total_comment_count = 0

        for post in posts:
            caption = post.get('caption', '')
            area_found = extract_area(caption)
            if area_found:
                # Save post row
                writer.writerow({
                    'type': 'post',
                    'post_id': post.get('id'),
                    'caption': caption,
                    'post_timestamp': post.get('timestamp', ''),
                    'media_url': post.get('media_url', ''),
                    'permalink': post.get('permalink', ''),
                    'comment_id': '',
                    'username': '',
                    'comment_text': '',
                    'comment_timestamp': '',
                    'area_mentioned': area_found
                })
                relevant_post_count += 1

            # Fetch comments for this post
            comments = fetch_comments(post['id'])
            for comment in comments:
                text = comment.get('text', '')
                area_in_comment = extract_area(text)
                if area_in_comment:
                    writer.writerow({
                        'type': 'comment',
                        'post_id': post.get('id'),
                        'caption': caption,
                        'post_timestamp': post.get('timestamp', ''),
                        'media_url': post.get('media_url', ''),
                        'permalink': post.get('permalink', ''),
                        'comment_id': comment.get('id'),
                        'username': comment.get('username', ''),
                        'comment_text': text,
                        'comment_timestamp': comment.get('timestamp', ''),
                        'area_mentioned': area_in_comment
                    })
                    total_comment_count += 1

    print(f"✅ {relevant_post_count} posts and {total_comment_count} comments with area mentions saved to {combined_file}")

# Run everything
if __name__ == "__main__":
    print("📥 Fetching Hyderabad Real Estate Instagram posts and comments mentioning areas...")
    posts = fetch_posts(limit=60)
    if posts:
        save_data_combined(posts)
    else:
        print("❌ No posts found or API error.")
