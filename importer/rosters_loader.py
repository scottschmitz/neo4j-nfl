from roster_loader import RosterLoader
import os

class RostersLoader:
  def __init__(self, db):
    self.db = db

  def load_all_rosters(self):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.join(script_dir, "scraper", "rawdata")

    year_dirs = [d for d in os.listdir(raw_data_path) 
      if os.path.isdir(os.path.join(raw_data_path, d)) and d.isdigit()]
    
    for year_dir in year_dirs:
      year_path = os.path.join(raw_data_path, year_dir, "teams")
      year = int(year_dir)

      try:
        team_dirs = [d for d in os.listdir(year_path) 
          if os.path.isdir(os.path.join(year_path, d))]
        
        for team_dir in team_dirs:
          team_path = os.path.join(year_path, team_dir)
          roster_path = os.path.join(team_path, "roster.csv")
          games_path = os.path.join(team_path, "games.csv")

          RosterLoader(self.db).load_team_data(
            year, 
            team_dir, 
            roster_path,
            games_path
          )
      except FileNotFoundError:
        print(f"No teams found for {year}")
        continue
        