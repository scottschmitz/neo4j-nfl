from draft_loader import DraftLoader
import os

class DraftsLoader:
  def __init__(self, db):
    self.db = db

  def load_all_drafts(self):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.join(script_dir, "scraper", "rawdata")

    year_dirs = [d for d in os.listdir(raw_data_path) 
      if os.path.isdir(os.path.join(raw_data_path, d)) and d.isdigit()]
    
    for year_dir in year_dirs:
      year = int(year_dir)
      draft_path = os.path.join(raw_data_path, year_dir, "draft", "draft.csv")

      DraftLoader(self.db).load_draft(
        year, 
        draft_path
      )