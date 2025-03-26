import os
import pandas as pd
from scraper.meta_data import team_abbr_to_id

class DraftLoader:
  def __init__(self, db):
    self.db = db

  def load_draft(self, year, draft_path):
    print(f"Loading data for {year} draft...")
    draft_df = pd.read_csv(draft_path)

    query = "MERGE(d:Draft {id: $draft_id, year: $year})"
    params = { 
      "draft_id": f"Draft_{year}", 
      "year": year 
    }
    self.db.run_query(query, params)
    print(f"✅ Created Draft year {year} complete.")

    # loop from 1-7
    for i in range(1, 8):
      query = """
        MATCH (d:Draft {year: $year})
        MERGE (r:Round {id: $round_id, year: $year, number: $round_number})
        MERGE (d)-[:HAS_ROUND]->(r)
      """
      params = { 
        "round_id": f"{year}_{i}",
        "year": year,
        "round_number": i
      }
      self.db.run_query(query, params)
    
    current_round = 0
    current_pick_in_round = 0
    for _, row in draft_df.iterrows():     
      round = int(row['Rnd'])
      overall_pick_number = int(row['Pick'])

      if current_round != round:
        current_round = round
        current_pick_in_round = 1
      else: 
        current_pick_in_round += 1

      query = """
        MATCH (d:Draft {year: $year})-[:HAS_ROUND]->(r:Round {number: $round_number})
        MERGE (p:Pick {id: $pick_id, year: $year, pick_number_in_round: $pick_number_in_round, overall_pick_number: $overall_pick_number})
        MERGE (r)-[:HAS_PICK]->(p)
      """
      params = { 
        "year": year,
        "round_number": round,
        "pick_id": f"{year}_{round}_{overall_pick_number}",
        "pick_number_in_round": current_pick_in_round,
        "overall_pick_number": overall_pick_number,
      }
      self.db.run_query(query, params)

      # Extract name parts
      name_parts = str(row['Player']).split(' ')
      first_name = name_parts[0] if len(name_parts) > 0 else ''
      last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
      last_name_cleaned = last_name.lower().replace(' ', '_')
    
      # Create player ID
      player_id = f"{first_name.lower()}_{last_name_cleaned.lower()}"

      pos = row['Pos']
      college = row['College/Univ']

      team_abbr = row['Tm'].lower()
      team_id = team_abbr_to_id[team_abbr]

      query = """
        MATCH (pick:Pick {year: $year, overall_pick_number: $overall_pick_number})
        MATCH (team:Team {id: $team_id})
        MERGE (team)-[:OWNS_PICK]->(pick)      
      """
      params = {
        "overall_pick_number": overall_pick_number,
        "team_id": team_id,
        "year": year,
      }
      self.db.run_query(query, params)

      query = """
        MERGE (player:Player {id: $player_id})
        ON CREATE SET 
          player.last_name = $last_name,
          player.first_name = $first_name
        WITH player
        MATCH (c:College {name: $college})
        MERGE (player)-[:DRAFTED_FROM {year: $year}]->(c)
        WITH player
        MATCH (pick:Pick {year: $year, overall_pick_number: $overall_pick_number})
        MERGE (pick)-[:SELECTED]->(player)
      """
      params = {
        "player_id": player_id,
        "last_name": last_name,
        "first_name": first_name,
        "round_number": round,
        "overall_pick_number": overall_pick_number,
        "team_id": team_id,
        "year": year,
        "college": college
      }
      self.db.run_query(query, params)
    print(f"✅ Draft year {year} complete.")

