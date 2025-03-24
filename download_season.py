import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import time

def parse_response(response):
  if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    content = re.sub(r'<!--\s*<tr class="thead">', '', content)
    content = re.sub(r'<!--\s*<tr class="over_header">', '', content)
    content = re.sub(r'<!--', '', content)
    content = re.sub(r'-->', '', content)

    return BeautifulSoup(content, 'html.parser')
  else:
    print(f"Failed to fetch page. Status code: {response.status_code}")
    return None
  
def extract_table_to_df(soup, table_id):
  table = soup.find("table", id=table_id)
  if table is None:
    print(f"Table '{table_id}' not found")
    return None

  last_row = table.find("thead").find_all("tr")[-1]
  if last_row is None:
    print(f"Table '{table_id}' has no headers")
    return None

  headers = [th.text.strip() for th in last_row.find_all("th")]

  rows = []
  for tr in table.find("tbody").find_all("tr"):
    if "class" in tr.attrs and ("thead" in tr["class"] or "divider" in tr["class"]):
      continue

    row = [td.get_text(separator=" ", strip=True).replace('\n', ' ').replace('\r', ' ') for td in tr.find_all(["td", "th"])]
    if row and len(row) == len(headers):
      rows.append(row)

  df = pd.DataFrame(rows, columns=headers)
  return df

def clean_dataframe(df):
  if df is None:
    return None
  
  # Clean columns
  df.columns = [col.strip() for col in df.columns]

  # Replace empty strings with NaN
  df = df.replace('', pd.NA)

  # Strip whitespace from all cells
  df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

  return df

pd.set_option('display.max_columns', None)

year = 2024
team_abbrs = [
  # 'buf', 'mia', 'nyj', 'nwe', # ACF East
  'rav', 'cin', 'cle', 'pit', # ACF North
  'htx', 'clt', 'jax', 'oti', # ACF South
  'den', 'kan', 'rai', 'sdg', # ACF West
  'dal', 'nyg', 'phi', 'was', # NFC East
  'chi', 'det', 'gnb', 'min', # NFC North
  'atl', 'car', 'nor', 'tam', # NFC South
  'crd', 'ram', 'sfo', 'sea'  # NFC West
]

team_abbr_to_id = {
    'buf': 'buffalo_bills',
    'mia': 'miami_dolphins',
    'nyj': 'new_york_jets',
    'nwe': 'new_england_patriots',
    'rav': 'baltimore_ravens',
    'cin': 'cincinnati_bengals',
    'cle': 'cleveland_browns',
    'pit': 'pittsburgh_steelers',
    'htx': 'houston_texans',
    'clt': 'indianapolis_colts',
    'jax': 'jacksonville_jaguars',
    'oti': 'tennessee_titans',
    'den': 'denver_broncos',
    'kan': 'kansas_city_chiefs',
    'rai': 'las_vegas_raiders',
    'sdg': 'los_angeles_chargers',
    'dal': 'dallas_cowboys',
    'nyg': 'new_york_giants',
    'phi': 'philadelphia_eagles',
    'was': 'washington_commanders',
    'chi': 'chicago_bears',
    'det': 'detroit_lions',
    'gnb': 'green_bay_packers',
    'min': 'minnesota_vikings',
    'atl': 'atlanta_falcons',
    'car': 'carolina_panthers',
    'nor': 'new_orleans_saints',
    'tam': 'tampa_bay_buccaneers',
    'crd': 'arizona_cardinals',
    'ram': 'los_angeles_rams',
    'sfo': 'san_francisco_49ers',
    'sea': 'seattle_seahawks'
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

# Automatically sleeps to stay within rate limits (20 requests per minute)
for team_abbr in team_abbrs:
  output_dir = f'rawdata/{year}/{team_abbr_to_id[team_abbr]}'
  os.makedirs(output_dir, exist_ok=True)

  print(f"Pulling data for {team_abbr}...")

  games_url = f"https://www.pro-football-reference.com/teams/{team_abbr}/{year}.htm"
  games_response = requests.get(games_url,headers=headers)
  games_soup = parse_response(games_response)
  games = extract_table_to_df(games_soup, 'games')
  if games is not None:
    csv_path = f"{output_dir}/games.csv"
    games.to_csv(csv_path, index=False)
    print(f"Successfully downloaded 'games' table")

  roster_url = f"https://www.pro-football-reference.com/teams/{team_abbr}/{year}_roster.htm"
  roster_response = requests.get(roster_url, headers=headers)
  roster_soup = parse_response(roster_response)
  roster_df = extract_table_to_df(roster_soup, 'roster')
  roster_df = clean_dataframe(roster_df)
  if roster_df is not None:
    csv_path = f"{output_dir}/roster.csv"
    roster_df.to_csv(csv_path, index=False)
    print(f"Successfully downloaded 'roster' table.")
  
  # sleep for 8 seconds so we stay uner 16 requests per minute
  # to be safely within the rate limit guidelines of 20
  print("Sleeping for 8 seconds...\n")
  time.sleep(8)