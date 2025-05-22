import os
import aiohttp
import asyncio
import csv
from datetime import datetime

PERPLEXITY_API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"

areas = [
    "kukatpally", "balanagar", "begumpet", "madhapur", "gachibowli", "banjara hills", "jubilee hills",
    "hitec city", "tarnaka", "sainikpuri", "langar houz", "himayatnagar", "ameerpet",
    "uppal", "narapally", "lb nagar", "nagole", "alwal", "kompally", "bowenpally", "shamirpet",
    "secunderabad", "kphb", "nizampet", "bachupally", "miyapur", "chandanagar", "patancheru",
    "beeramguda", "mallampet", "gandimaisamma", "suraram", "medchal", "attapur", "rajendranagar",
    "mehdipatnam", "manikonda", "puppalaguda", "nanakramguda", "financial district", "kokapet",
    "osman nagar", "tellapur", "gopanpally", "narsingi", "serilingampally", "amberpet",
    "erragadda", "moosapet", "motinagar", "errum manzil", "malakpet", "santoshnagar",
    "balapur", "bandlaguda jagir", "kismatpur", "bahadurpura", "shamshabad", "abids",
    "malkajgiri", "nacharam", "habshiguda", "ramanthapur", "safilguda",
    "moula ali", "ecil", "dilsukhnagar", "chintalkunta", "kollur", "raviryal",
    "ghatkesar", "kancha gachibowli", "kondapur", "kandukur", "chevella", "tukkuguda",
    "ibrahimpatnam", "moinabad", "adibatla", "pocharam", "bongloor", "muthangi",
    "isnapur", "chegunta", "bibinagar", "turkapally", "khairatabad", "moosapet",
    "adibatla", "khajaguda", "boduppal", "rampally", "yapral",
]

def generate_prompts(area):
    return [
        f"List the latest real estate projects happening in {area}, including positive developments and any challenges or negative aspects.",
        f"Describe current government infrastructure developments in {area}, mentioning progress as well as any delays or issues.",
        f"Are there upcoming investment plans, SEZ zones, or expansion activities in {area}? Include potential risks or concerns.",
        f"List available facilities (schools, hospitals, malls, etc.) in {area}, and mention any shortcomings or lacking amenities.",
        f"How well-connected is {area} to work hubs, schools, hospitals, and transport? Include buses, trains, metro, roads, traffic, and any connectivity problems or gaps.",
        f"List the main risks or threats currently affecting the real estate market and infrastructure in {area}.",
        f"List the key gaps, shortcomings, or missing elements in real estate, infrastructure, or amenities in {area}.",
    ]

async def ask_perplexity(session, prompt):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        async with session.post(API_URL, headers=headers, json=payload, timeout=60) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error with prompt '{prompt}': {e}")
        return ""

async def fetch_area_data(session, area):
    prompts = generate_prompts(area)
    keys = [
        "Projects", "Govt_Developments", "Planning", "Facilities", "Connectivity", "Risks", "Gaps"
    ]
    row = {"Location": area}
    for i, key in enumerate(keys):
        print(f"Fetching {key} info for {area}...")
        result = await ask_perplexity(session, prompts[i])
        row[key] = result
    return row

async def collect_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_area_data(session, area) for area in areas]
        all_data = await asyncio.gather(*tasks)
    return all_data

def save_to_csv(data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"scraping/data/real_estate_perplexity_data_{timestamp}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline='', encoding='utf-8') as f:
        fieldnames = [
            "Location", "Projects", "Govt_Developments", "Planning",
            "Facilities", "Connectivity", "Risks", "Gaps"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Saved data to {filename}")

if __name__ == "__main__":
    print("Starting data extraction from Perplexity API...")
    data = asyncio.run(collect_all_data())
    save_to_csv(data)