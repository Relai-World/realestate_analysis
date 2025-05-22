import re
import tweepy
import logging
from textblob import TextBlob
from collections import defaultdict
import pandas as pd

# =================== CONFIG ===================
CONFIG = {
    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAAG2R1AEAAAAAIBJmm8oQVQA9Oo6sInxNo%2F9sNJc%3DVTB4sZxiN5qrkNt8a1BfKushkUBdCxTAomDL9PoysJoIV1TvzR',
    'tweet_count': 100,
    'export_csv': True,
    'csv_filename': 'hyderabad_real_estate_analysis.csv',
}

HYD_LOCALITIES = [
    'Gachibowli', 'HITEC City', 'Madhapur', 'Kondapur', 'Kokapet', 'Banjara Hills',
    'Jubilee Hills', 'Somajiguda', 'Neopolis', 'Narsingi', 'Tellapur',
    'Lingampally', 'Miyapur', 'Kukatpally', 'Secunderabad', "hyderabad", "kukatpally", "madhapur", "gachibowli", "banjara hills", "jubilee hills", "hitec city", "tarnaka",
    "sainikpuri", "langar houz", "himayatnagar", "ameerpet", "begumpet", "uppal", "narapally", "lb nagar", "nagole",
    "alwal", "kompally", "bowenpally", "shamirpet", "secunderabad", "adilabad", "kphb", "nizampet", "bachupally",
    "miyapur", "chandanagar", "patancheru", "beeramguda", "mallampet", "gandimaisamma", "suraram", "medchal",
    "attapur", "rajendranagar", "mehdipatnam", "manikonda", "puppalaguda", "nanakramguda", "financial district",
    "kokapet", "osman nagar", "tellapur", "gopanpally", "narsingi", "serilingampally", "amberpet", "erragadda",
    "moosapet", "motinagar", "errum manzil", "malakpet", "santoshnagar", "balapur", "bandlaguda jagir", "kismatpur",
    "bahadurpura", "shamshabad", "abids", "malkajgiri", "nacharam", "habshiguda", "ramanthapur", "kapra",
    "safilguda", "moula ali", "ECIL", "dilsukhnagar", "chintalkunta", "kollur", "raviryal", "ghatkesar",
    "kancha gachibowli", "kondapur", "kandukur", "chevella", "tukkuguda", "ibrahimpatnam", "moinabad",
    "adibatla", "pocharam", "bongloor", "muthangi", "isnapur", "chegunta", "bibinagar", "turkapally"
    "shadnagar", "shamshabad", "medchal", "nagole", "kothapet", "malkajgiri","sainikpuri",
]

SUITABILITY_KEYWORDS = {
    'living': ['residential', 'housing', 'apartments', 'good for living', 'family', 'amenities', 'safe', 'clean'],
    'commercial': ['office', 'commercial', 'business', 'shops', 'retail', 'leasing', 'co-working'],
    'industrial': ['industrial', 'warehousing', 'manufacturing', 'logistics', 'factory']
}

REASON_KEYWORDS = {
    'infrastructure': ['metro', 'roads', 'connectivity', 'airport', 'expressway'],
    'pricing': ['affordable', 'expensive', 'price', 'cost', 'budget'],
    'amenities': ['schools', 'hospitals', 'malls', 'parks', 'gyms'],
    'growth': ['development', 'investment', 'boom', 'growth', 'upcoming']
}


# =================== LOGGER ===================
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# ============ TWITTER CLIENT ================
class TwitterClient:
    def __init__(self):
        try:
            self.client = tweepy.Client(
                bearer_token=CONFIG['bearer_token']
            )
            logging.info("Twitter client authenticated successfully with Bearer Token.")
        except Exception as e:
            logging.error(f"Authentication Failed: {str(e)}")
            raise

    def fetch_tweets(self, query, count=100):
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, 100),
                tweet_fields=['public_metrics', 'created_at']
            )
            return response.data or []
        except tweepy.TweepyException as e:
            logging.error(f"Error fetching tweets: {str(e)}")
            return []


# ========== TEXT ANALYSIS UTILITIES ============
def clean_tweet(tweet):
    tweet = re.sub(r"http\S+|@\S+|#[^\s]+", "", tweet)
    tweet = re.sub(r"[^A-Za-z0-9\s]", " ", tweet)
    tweet = re.sub(r"\s+", " ", tweet).strip()
    return tweet.lower()


def get_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def extract_locations(tweet):
    return [loc for loc in HYD_LOCALITIES if re.search(r'\b' + re.escape(loc) + r'\b', tweet, re.IGNORECASE)]


def extract_tags(tweet, keyword_dict):
    tags = set()
    tweet_lower = tweet.lower()
    for category, keywords in keyword_dict.items():
        if any(keyword in tweet_lower for keyword in keywords):
            tags.add(category)
    return list(tags) if tags else ['unspecified']


# ========== ANALYSIS PIPELINE ============
def analyze_tweets(tweets):
    location_stats = defaultdict(lambda: {
        'positive': 0, 'negative': 0, 'neutral': 0,
        'suitability': defaultdict(int),
        'reasons': defaultdict(int),
        'total': 0
    })

    records = []

    for tweet_obj in tweets:
        text = tweet_obj.text
        sentiment = get_sentiment(text)
        locations = extract_locations(text)
        suitability = extract_tags(text, SUITABILITY_KEYWORDS)
        reasons = extract_tags(text, REASON_KEYWORDS)

        for loc in locations:
            stats = location_stats[loc]
            stats[sentiment] += 1
            stats['total'] += 1
            for suit in suitability:
                stats['suitability'][suit] += 1
            for reason in reasons:
                stats['reasons'][reason] += 1

        records.append({
            'tweet': text,
            'sentiment': sentiment,
            'locations': ', '.join(locations),
            'suitability': ', '.join(suitability),
            'reasons': ', '.join(reasons)
        })

    # Summary
    summary = []
    for loc, data in location_stats.items():
        pos, neg, neu = data['positive'], data['negative'], data['neutral']
        total = data['total']
        summary.append({
            'Location': loc,
            'Total Tweets': total,
            'Positive (%)': round((pos / total) * 100, 2),
            'Negative (%)': round((neg / total) * 100, 2),
            'Neutral (%)': round((neu / total) * 100, 2),
            'Primary Suitability': max(data['suitability'], key=data['suitability'].get, default='unknown'),
            'Top Reasons': ', '.join(sorted(data['reasons'], key=data['reasons'].get, reverse=True)[:3])
        })

    return summary, records


# ========== MAIN RUNNER ============
def main():
    logging.info("Starting Hyderabad real estate tweet analysis...")

    api = TwitterClient()
    query = '("Hyderabad real estate" OR "Hyderabad property" OR "Hyderabad housing" OR "Hyderabad commercial") -is:retweet lang:en'
    tweets = api.fetch_tweets(query, CONFIG['tweet_count'])

    if not tweets:
        logging.warning("No tweets retrieved. Check your Bearer Token or internet.")
        return

    summary, records = analyze_tweets(tweets)

    logging.info("\n=== AREA-WISE REAL ESTATE ANALYSIS ===\n")
    for row in summary:
        logging.info(f"📍 {row['Location']}: {row['Positive (%)']}% positive, "
                     f"{row['Negative (%)']}% negative, Primary use: {row['Primary Suitability']}, "
                     f"Reasons: {row['Top Reasons']}")

    if CONFIG['export_csv']:
        df_summary = pd.DataFrame(summary)
        df_records = pd.DataFrame(records)
        df_summary.to_csv("summary_" + CONFIG['csv_filename'], index=False)
        df_records.to_csv("tweets_" + CONFIG['csv_filename'], index=False)
        logging.info(f"\nCSV exported: summary_{CONFIG['csv_filename']} and tweets_{CONFIG['csv_filename']}")


if __name__ == "__main__":
    main()
