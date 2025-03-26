import pandas as pd
import requests
from bs4 import BeautifulSoup
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

def make_soup(url):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
  }
  response = requests.get(url, headers=headers)
  return parse_response(response)

def make_csv(soup, table_name, csv_path):
  df = extract_table_to_df(soup, table_name)
  if df is not None:
    df.to_csv(csv_path, index=False)
    print(f"Successfully downloaded '{table_name}' table")