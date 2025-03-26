import pandas as pd

class RosterLoader:
  def __init__(self, db):
    self.db = db
        
  def load_team_data(self, season_year, team_id, roster_file_path, games_file_path):
    """
    Load team data from CSV files

    Args:
      season_year: The NFL season year (e.g., 2024)
      team_id: Team identifier (e.g., 'detroit_lions')
      roster_file_path: Path to roster CSV file
      games_file_path: Path to games CSV file
    """
    print(f"Loading data for {team_id} in {season_year}...")
    
    # Read CSV files
    roster_df = pd.read_csv(roster_file_path)
    games_df = pd.read_csv(games_file_path)

    # Load positions
    self._load_positions(roster_df)

    # Load colleges
    self._load_colleges(roster_df)

    # Load players
    self._load_players(roster_df, season_year, team_id)

    # Load games
    self._load_games(games_df, season_year, team_id)

    print(f"✅ {team_id} complete.")

  def _load_positions(self, roster_df):
    """Extract and create position nodes"""
    # Extract unique positions
    positions = set()
    for position_list in roster_df['Pos'].dropna():
      for position in position_list.replace('"', '').split(','):
        clean_position = position.strip()
        if clean_position:
          positions.add(clean_position)
        
    # Create positions in batch
    for i in range(0, len(positions), 50):  # Process in batches of 50
      batch = list(positions)[i:i+50]
      query = """
        UNWIND $positions AS position_name
        MERGE (p:Position {name: position_name});
      """
      self.db.run_query(query, {"positions": batch})
        
  def _load_colleges(self, roster_df):
    """Extract and create college nodes"""
    # Extract unique colleges
    colleges = set()
    for college_list in roster_df['College/Univ'].dropna():
      for college in college_list.replace('"', '').split(','):
        clean_college = college.strip()
        if clean_college:
          colleges.add(clean_college)
        
    # Create colleges in batch
    for i in range(0, len(colleges), 50):  # Process in batches of 50
      batch = list(colleges)[i:i+50]
      query = """
        UNWIND $colleges AS college_name
        MERGE (c:College {name: college_name});
      """
      self.db.run_query(query, {"colleges": batch})
        
  def _load_players(self, roster_df, season_year, team_id):
    """Create player nodes and relationships"""
    # Process each player
    for _, row in roster_df.iterrows():
      if pd.isna(row['Player']):
        continue
                
      # Format birthdate
      if not pd.isna(row['BirthDate']) and row['BirthDate'] != '':
        formatted_date = row['BirthDate'].replace('/', '').replace(' ', '').replace(',', '')
      else:
        formatted_date = 'unknown'
                
      # Extract name parts
      name_parts = str(row['Player']).split(' ')
      first_name = name_parts[0] if len(name_parts) > 0 else ''
      last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
      last_name_cleaned = last_name.lower().replace(' ', '_')
    
      # Create player ID
      player_id = f"{first_name.lower()}_{last_name_cleaned.lower()}_{formatted_date}"
    
      # Jersey number
      number = None if pd.isna(row['No.']) else str(row['No.'])
            
      # Create player
      query = """
        MERGE (p:Player {id: $player_id})
        ON CREATE SET 
          p.last_name = $last_name,
          p.first_name = $first_name,
          p.birthdate = $formatted_date,
          p.number = $number
              
        WITH p
        MATCH (t:Team {id: $team_id})
        MERGE (p)-[r:PLAYS_FOR {season: $season_year}]->(t)
      """
      params = {
        "player_id": player_id,
        "last_name": last_name,
        "first_name": first_name,
        "formatted_date": formatted_date,
        "number": number,
        "team_id": team_id,
        "season_year": season_year
      }
      self.db.run_query(query, params)
            
      # Connect player to colleges
      if not pd.isna(row['College/Univ']):
        colleges = [college.strip() for college in row['College/Univ'].replace('"', '').split(',') if college.strip()]
        if colleges:
          query = """
            MATCH (p:Player {id: $player_id})
            UNWIND $colleges AS college_name
            MATCH (c:College {name: college_name})
            MERGE (p)-[:ATTENDED]->(c)
          """
          self.db.run_query(query, {"player_id": player_id, "colleges": colleges})

      if not pd.isna(row['Pos']):
        pos = row['Pos'].strip()
        if pos:
          query = """
            MATCH (p:Player {id: $player_id})
            MATCH (pos:Position {name: $position})
            MERGE (p)-[:PLAYS]->(pos)
          """
          self.db.run_query(query, {"player_id": player_id, "position": pos})
    
  def _load_games(self, games_df, season_year, team_id):
    """Create game nodes and relationships"""
    # Filter for home games
    home_games = games_df[games_df['Location'].isna() & ~games_df['Day'].isna() & (games_df['Day'] != '')]
        
    for _, row in home_games.iterrows():
      opponent = str(row['Opp']).lower().replace(' ', '_').replace('.', '')
      game_id = f"{season_year}_week_{row['Week']}_{team_id}_{opponent}"
            
      # Scores
      home_score = None if pd.isna(row['ScoreTm']) else int(row['ScoreTm'])
      away_score = None if pd.isna(row['ScoreOpp']) else int(row['ScoreOpp'])
      
      # Create game
      query = """
      MERGE (g:Game {gameId: $game_id})
      ON CREATE SET
        g.date = $date,
        g.time = $time,
        g.dayOfWeek = $day_of_week,
        g.homeTeam = $team_id,
        g.awayTeam = $opp_id,
        g.homeScore = $home_score,
        g.awayScore = $away_score
          
      WITH g
      MATCH (home_team:Team {id: $team_id})
      MERGE (home_team)-[home:WAS_HOME]->(g)
      
      WITH g
      MATCH (w:Week {id: $week_id})
      MERGE (g)-[:IN_WEEK]->(w)
      
      WITH g
      MATCH (home_team:Team {id: $team_id})
      MATCH (stadium:Stadium)<-[:PLAYS_AT]-(home_team)
      MERGE (g)-[:PLAYED_AT]->(stadium)
      """
      params = {
        "game_id": game_id,
        "date": row['Date'],
        "time": row['Time'],
        "day_of_week": row['Day'],
        "team_id": team_id,
        "opp_id": opponent,
        "home_score": home_score,
        "away_score": away_score,
        "week_id": f"{season_year}_week_{int(row['Week'])}"
      }
      self.db.run_query(query, params)
      
      # Connect away team      
      query = """
      MATCH (g:Game {gameId: $game_id})
      MATCH (awayTeam:Team)
      WHERE awayTeam.id = $opp_id OR 
        REPLACE(LOWER(awayTeam.name), ' ', '_') = $opp_id OR
        REPLACE(LOWER(awayTeam.full_name), ' ', '_') = $opp_id
      MERGE (awayTeam)-[away:WAS_AWAY]->(g)
      """
      params = {
        "game_id": game_id,
        "opp_id": opponent
      }
      self.db.run_query(query, params)