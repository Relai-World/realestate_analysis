import os
import pandas as pd
import streamlit as st
import asyncio
import httpx
import re

# === CONFIGURATION ===
PERPLEXITY_API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"
CSV_PATH = r"C:\Users\Medis\OneDrive\Documents\Desktop\real_estate_trend\scraping\scraping\data\real_estate_perplexity_data_20250521_2135.csv"
CONCURRENCY = 5

BLUE = "#1557FF"
BLACK = "#000000"
WHITE = "#FFFFFF"
CARD_BG = "#F8F9FB"  # Light card background

TEXT_FIELDS = [
    "Projects",
    "Govt_Developments",
    "Planning",
    "Facilities",
    "Connectivity",
    "Risks",
    "Gaps"
]

def combine_area_text(row):
    return " ".join([str(row[field]) for field in TEXT_FIELDS if pd.notna(row.get(field, None))])

def robust_sentiment_extraction(result):
    sentiment, reason = "Unknown", ""
    result_lower = result.lower()
    if "positive" in result_lower:
        sentiment = "Positive"
    elif "negative" in result_lower:
        sentiment = "Negative"
    elif "neutral" in result_lower:
        sentiment = "Neutral"
    if '.' in result:
        parts = result.split('.', 1)
        if len(parts) == 2:
            candidate, candidate_reason = parts
            if candidate.strip().lower() in ["positive", "negative", "neutral"]:
                sentiment = candidate.strip().capitalize()
                reason = candidate_reason.strip()
            else:
                reason = result
        else:
            reason = result
    else:
        reason = result
    return sentiment, reason

async def ask_perplexity_async(client, prompt):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be concise and precise."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        resp = await client.post(API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"API Error: {e}"

async def run_sentiment_analysis_async(df, progress_callback=None):
    results = []
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient() as client:
        async def process_row(idx, row):
            async with sem:
                combined_text = combine_area_text(row)
                prompt = (
                    f"Analyze the sentiment of the following text about {row['Location']} and classify it as Positive, Negative, or Neutral. "
                    f"Also provide a brief reason for your classification.\n\nText: \"{combined_text}\""
                )
                result = await ask_perplexity_async(client, prompt)
                sentiment, reason = robust_sentiment_extraction(result)
                if progress_callback:
                    progress_callback(idx + 1)
                return {
                    "Location": row["Location"],
                    "Sentiment": sentiment,
                    "Reason": reason,
                    "Combined_Text": combined_text
                }
        tasks = [process_row(idx, row) for idx, row in df.iterrows()]
        for coro in asyncio.as_completed(tasks):
            results.append(await coro)
    return pd.DataFrame(results)

def get_least_facilities_connectivity(df, n=10):
    def score(text):
        text = str(text).lower()
        keywords = ['no', 'not', 'lack', 'missing', 'poor', 'inadequate', 'insufficient', 'limited', 'few', 'scarce']
        return sum(k in text for k in keywords)
    df['Facilities_Gap_Score'] = df['Facilities'].apply(score)
    df['Connectivity_Gap_Score'] = df['Connectivity'].apply(score)
    facilities_gaps = df.sort_values('Facilities_Gap_Score', ascending=False).head(n)
    connectivity_gaps = df.sort_values('Connectivity_Gap_Score', ascending=False).head(n)
    return facilities_gaps, connectivity_gaps

def chat_with_perplexity(user_query, area_df):
    area_names = area_df["Location"].tolist()
    area_in_query = None
    for area in area_names:
        if re.search(rf"\b{re.escape(area)}\b", user_query, re.IGNORECASE):
            area_in_query = area
            break

    if area_in_query:
        area_row = area_df[area_df["Location"].str.lower() == area_in_query.lower()].iloc[0]
        area_text = "\n".join([f"{field}: {area_row[field]}" for field in TEXT_FIELDS])
        context = f"Here is the data for {area_in_query}:\n{area_text}"
    else:
        context = "No matching area in local data. Please use real-time web search."

    prompt = (
        "You are a Hyderabad real estate expert assistant. "
        "If the answer is in the provided data context, use it. "
        "Otherwise, search the web and provide a brief, realistic, and up-to-date answer with recent facts, trends, or news. "
        "Keep your answer simple and cite web sources if possible.\n"
        f"User query: {user_query}\n\n"
        f"Data context:\n{context}"
    )

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be concise, precise, and cite web sources if possible."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    try:
        resp = httpx.post(API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Sorry, I couldn't fetch an answer from Perplexity AI right now. Please try again later."

def main():
    # --- Custom CSS for branding, white background, and card-like sections ---
    st.markdown(f"""
        <style>
        body {{
            background-color: {WHITE};
        }}
        .relai-title {{
            font-size: 2.8rem;
            font-weight: 900;
            color: {BLUE};
            letter-spacing: -2px;
            margin-bottom: 0.1em;
            margin-top: 0.5em;
        }}
        .subtitle {{
            font-size: 1.2rem;
            color: {BLACK};
            margin-bottom: 2em;
        }}
        .card {{
            background: {CARD_BG};
            border-radius: 18px;
            padding: 1.5em 1em 1em 1em;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 8px rgba(21,87,255,0.06);
        }}
        .stDataFrame th, .stDataFrame td {{
            color: {BLACK} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="relai-title">relai.</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">hyderabad realestate analysis</div>', unsafe_allow_html=True)

    if not os.path.exists(CSV_PATH):
        st.error(f"CSV file not found at {CSV_PATH}")
        return
    df = pd.read_csv(CSV_PATH)

    # Run sentiment analysis if missing or empty
    if "Sentiment" not in df.columns or df["Sentiment"].isnull().all():
        st.info("Running Perplexity AI sentiment analysis. This might take a while...")
        progress_bar = st.progress(0)
        total = len(df)
        def progress_callback(done):
            progress_bar.progress(done / total)
        sentiment_df = asyncio.run(run_sentiment_analysis_async(df, progress_callback))
        df = df.merge(sentiment_df[["Location", "Sentiment", "Reason"]], on="Location", how="left")
        df.to_csv(CSV_PATH, index=False)
        st.success("Sentiment analysis completed and saved.")

    # Section: Area-wise Government Developments
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:{BLUE};margin-bottom:0.5em;'>Area-wise Government Developments</h4>", unsafe_allow_html=True)
    if "Govt_Developments" in df.columns:
        st.dataframe(df[["Location", "Govt_Developments"]], use_container_width=True)
    else:
        st.warning("Govt_Developments column missing.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Section: Area-wise Facilities
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:{BLUE};margin-bottom:0.5em;'>Area-wise Facilities</h4>", unsafe_allow_html=True)
    if "Facilities" in df.columns:
        st.dataframe(df[["Location", "Facilities"]], use_container_width=True)
    else:
        st.warning("Facilities column missing.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Section: Area-wise Connectivity
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:{BLUE};margin-bottom:0.5em;'>Area-wise Connectivity</h4>", unsafe_allow_html=True)
    if "Connectivity" in df.columns:
        st.dataframe(df[["Location", "Connectivity"]], use_container_width=True)
    else:
        st.warning("Connectivity column missing.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Section: Least Facilities / Connectivity
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:{BLUE};margin-bottom:0.5em;'>Areas with Least Facilities / Connectivity</h4>", unsafe_allow_html=True)
    if "Facilities" in df.columns and "Connectivity" in df.columns:
        facilities_gaps, connectivity_gaps = get_least_facilities_connectivity(df)
        st.markdown("*Least Facilities*")
        st.dataframe(facilities_gaps[["Location", "Facilities", "Facilities_Gap_Score"]], use_container_width=True)
        st.markdown("*Least Connectivity*")
        st.dataframe(connectivity_gaps[["Location", "Connectivity", "Connectivity_Gap_Score"]], use_container_width=True)
    else:
        st.warning("Facilities or Connectivity columns missing.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Chatbot with conversation history ---
    st.sidebar.markdown(f"<div style='font-size:1.5rem;font-weight:900;color:{BLUE};margin-bottom:0.2em;'>relai.</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='font-size:1.1rem;color:{BLACK};margin-bottom:1em;'>Chat with Real Estate Data</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for chat in st.session_state.chat_history:
        st.sidebar.markdown(f"<span style='color:{BLACK};font-weight:600;'>You:</span> {chat['user']}", unsafe_allow_html=True)
        st.sidebar.markdown(f"<span style='color:{BLUE};font-weight:600;'>Bot:</span> {chat['bot']}", unsafe_allow_html=True)

    # User input
    user_query = st.sidebar.text_input("Type your question and press Enter:", key="chat_input")
    if st.sidebar.button("Send") and user_query.strip():
        with st.spinner("Getting answer from Perplexity AI..."):
            chat_response = chat_with_perplexity(user_query, df)
        st.session_state.chat_history.append({"user": user_query, "bot": chat_response})
        st.experimental_rerun()

if __name__ == "__main__":
    main()