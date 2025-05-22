import praw
import pandas as pd
import time
import re
from datetime import datetime

# Reddit API credentials (replace with your own)
reddit = praw.Reddit(
    client_id='RoJZd09TguwziCBEGOOmhw',
    client_secret='v5Da4H06Ub4f-V47EHQWy_HA0j_S_g',
    user_agent='hyd-realestate-scraper'
)

# Real estate related keywords
keywords = [
    'apartment', 'apartments', 'flats', 'flat', 'villa', 'villas', 'plot', 'plots', 'layout',
    'layouts', 'real estate', 'property', 'properties', 'metro', 'investment', 'invest', 'rent',
    'lease', 'ts govt project', 'rera', 'developer', 'developers', 'construction', 'housing',
    'gated community', 'gated communities', 'builder', 'builders', 'dtcp', 'hmda', 'open plot',
    'land rates', 'land price', 'land value', 'projects', 'developments', 'government',
    'govt', 'approval', 'sanction', 'registrations', 'clubhouse', 'club house', 'possession',
    'handover', 'loan', 'emi', 'emi holiday', 'pre launch', 'soft launch', 'launch offer',
    'open land', 'agriculture land', 'farm plot', 'commercial space', 'office space',
    'business park', 'it park', 'financial district', 'infra', 'infrastructure', 'inner ring road',
    'outer ring road', 'orr', 'airport connectivity', 'highway access', 'location advantage',
    'property rates', 'price hike', 'price drop', 'market value', 'property value', 'resale value',
    'future growth', 'township', 'master plan', 'luxury homes', 'budget apartment', 'ready to move',
    'under construction', 'possession date', 'rental yield', 'rental returns', 'open space',
    'amenities', 'schools nearby', 'hospitals nearby', 'supermarket nearby', 'future proof',
    'realty trends', 'property trends', 'hyd infra', 'smart city', 'town planning', 'municipal limits',
    'hmda approval', 'dtcp approval', 'clear title', 'legal issues', 'property dispute',
    'investment zone', 'growth corridor', 'commercial hub', 'it corridor'
]

# Hyderabad areas list
areas = [
    'hyderabad', 'kukatpally', 'madhapur', 'gachibowli', 'banjara hills', 'jubilee hills', 'raidurg',
    'sherlingampally', 'kondapur', 'miyapur', 'sainikpuri', 'hitec city', 'tarnaka', 'langar houz',
    'himayatnagar', 'ameerpet', 'begumpet', 'uppal', 'narapally', 'lb nagar', 'nagole', 'alwal',
    'kompally', 'bowenpally', 'shamirpet', 'secunderabad', 'adilabad', 'kphb', 'nizampet',
    'bachupally', 'chandanagar', 'patancheru', 'beeramguda', 'mallampet', 'gandimaisamma',
    'suraram', 'medchal', 'attapur', 'rajendranagar', 'mehdipatnam', 'manikonda', 'puppalaguda',
    'nanakramguda', 'financial district', 'kokapet', 'osman nagar', 'tellapur', 'gopanpally',
    'narsingi', 'serilingampally', 'amberpet', 'erragadda', 'moosapet', 'motinagar', 'errum manzil',
    'malakpet', 'santoshnagar', 'balapur', 'bandlaguda jagir', 'kismatpur', 'bahadurpura',
    'shamshabad', 'abids', 'malkajgiri', 'nacharam', 'habshiguda', 'ramanthapur', 'kapra',
    'safilguda', 'moula ali', 'ecil', 'dilsukhnagar', 'chintalkunta'
]

# Compile regex patterns for keywords and areas
keyword_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b', re.IGNORECASE)
area_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, areas)) + r')\b', re.IGNORECASE)

def clean_text(text):
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_matches(text, regex):
    matches = regex.findall(text)
    return ', '.join(sorted(set(matches))) if matches else None

def scrape_reddit(subreddits, limit=100):
    results = []
    for subreddit in subreddits:
        print(f"🔍 Scraping r/{subreddit} ...")
        try:
            for submission in reddit.subreddit(subreddit).hot(limit=limit):
                post_text = (submission.title or '') + ' ' + (submission.selftext or '')
                cleaned_post = clean_text(post_text)

                if area_pattern.search(cleaned_post) and keyword_pattern.search(cleaned_post):
                    post_keywords = extract_matches(cleaned_post, keyword_pattern)
                    post_areas = extract_matches(cleaned_post, area_pattern)
                    results.append({
                        'subreddit': subreddit,
                        'type': 'Post',
                        'content': submission.title.strip(),
                        'matched_keywords': post_keywords,
                        'matched_areas': post_areas,
                        'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d')
                    })

                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    comment_text = comment.body or ''
                    cleaned_comment = clean_text(comment_text)

                    if area_pattern.search(cleaned_comment) and keyword_pattern.search(cleaned_comment):
                        comment_keywords = extract_matches(cleaned_comment, keyword_pattern)
                        comment_areas = extract_matches(cleaned_comment, area_pattern)
                        results.append({
                            'subreddit': subreddit,
                            'type': 'Comment',
                            'content': comment.body.strip(),
                            'matched_keywords': comment_keywords,
                            'matched_areas': comment_areas,
                            'date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d')
                        })

        except Exception as e:
            print(f"⚠️ Error scraping r/{subreddit}: {e}")

    return results

# Subreddits to scrape
subreddits = [
    'hyderabad', 'Telangana', 'realestate', 'RealEstateIndia', 'hyderabadrealestate', 'RealEstateHyderabad'
]

# Run the scraper
data = scrape_reddit(subreddits, limit=100)

# Save results to CSV
df = pd.DataFrame(data)
df.to_csv('hyderabad_realestate_reddit_data.csv', index=False, encoding='utf-8-sig')

print(f"✅ Scraped {len(df)} posts/comments mentioning Hyderabad areas + real estate keywords. Saved to 'hyderabad_realestate_reddit_data.csv'")
