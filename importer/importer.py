from datetime import datetime
from dotenv import load_dotenv
from neo4j_helper import Neo4jHelper
from setup_nfl_league_info import NFLLeagueInfo
from setup_year import NflSeasonYear
from rosters_loader import RostersLoader
from drafts_loader import DraftsLoader
import os

# Load environment variables from .env
load_dotenv()

# Get credentials from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize the connection
db = Neo4jHelper(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Verify connection
try:
  db.driver.verify_connectivity()
  print("✅ Connected to Neo4j")
except Exception as e:
  print(f"❌ Connection failed: {e}")


NflSeasonYear(db).create(2024, datetime(2024, 9, 5), 18, 'LIX')
NFLLeagueInfo(db).create()

RostersLoader(db).load_all_rosters()

DraftsLoader(db).load_all_drafts()

# Close the connection when done
db.close()