class NFLLeagueInfo:
  def __init__(self, db):
      self.db = db

  def create(self):
    self.create_conferences()
    self.create_divisions()
    self.create_teams()
    self.create_stadiums()

  def create_conferences(self):
    query = """
      UNWIND [
        {id: 'afc', name: 'American Football Conference', abbr: 'AFC'},
        {id: 'nfc', name: 'National Football Conference', abbr: 'NFC'}
      ] AS conference_data
      MERGE (c:Conference {
        conference_id: conference_data.id,
        name: conference_data.name,
        abbreviation: conference_data.abbr
      });
    """
    self.db.run_query(query)

  def create_divisions(self):
    query = """
      UNWIND [
        {id: 'nfc_north', name: 'NFC North', conference: 'nfc'},
        {id: 'nfc_south', name: 'NFC South', conference: 'nfc'},
        {id: 'nfc_east', name: 'NFC East', conference: 'nfc'},
        {id: 'nfc_west', name: 'NFC West', conference: 'nfc'},
        {id: 'afc_north', name: 'AFC North', conference: 'afc'},
        {id: 'afc_south', name: 'AFC South', conference: 'afc'},
        {id: 'afc_east', name: 'AFC East', conference: 'afc'},
        {id: 'afc_west', name: 'AFC West', conference: 'afc'}
      ] AS division_data
      MERGE (d:Division {
        division_id: division_data.id,
        name: division_data.name
      })

      // Link Division to conference
      WITH d, division_data
      MATCH (c:Conference {conference_id: division_data.conference})
      MERGE (d)-[:BELONGS_TO]->(c);
    """
    self.db.run_query(query)

  def create_teams(self):
    query = """
      UNWIND [
        // NFC North
        {id: 'detroit_lions', city: 'Detroit', name: 'Lions', mascot: 'Roary the Lion', colors: ['Honolulu Blue', 'Silver'], division: 'nfc_north'},
        {id: 'chicago_bears', city: 'Chicago', name: 'Bears', mascot: 'Staley Da Bear', colors: ['Navy Blue', 'Orange'], division: 'nfc_north'},
        {id: 'green_bay_packers', city: 'Green Bay', name: 'Packers', mascot: null, colors: ['Dark Green', 'Gold'], division: 'nfc_north'},
        {id: 'minnesota_vikings', city: 'Minneapolis', name: 'Vikings', mascot: 'Viktor the Viking', colors: ['Purple', 'Gold'], division: 'nfc_north'},
        
        // NFC South
        {id: 'atlanta_falcons', city: 'Atlanta', name: 'Falcons', mascot: 'Freddie Falcon', colors: ['Black', 'Red'], division: 'nfc_south'},
        {id: 'carolina_panthers', city: 'Charlotte', name: 'Panthers', mascot: 'Sir Purr', colors: ['Black', 'Electric Blue'], division: 'nfc_south'},
        {id: 'new_orleans_saints', city: 'New Orleans', name: 'Saints', mascot: 'Gumbo the Dog', colors: ['Black', 'Gold'], division: 'nfc_south'},
        {id: 'tampa_bay_buccaneers', city: 'Tampa Bay', name: 'Buccaneers', mascot: 'Captain Fear', colors: ['Red', 'Pewter', 'Orange'], division: 'nfc_south'},
        
        // NFC East
        {id: 'dallas_cowboys', city: 'Dallas', name: 'Cowboys', mascot: 'Rowdy', colors: ['Navy Blue', 'Silver', 'White'], division: 'nfc_east'},
        {id: 'new_york_giants', city: 'New York', name: 'Giants', mascot: null, colors: ['Royal Blue', 'Red'], division: 'nfc_east'},
        {id: 'philadelphia_eagles', city: 'Philadelphia', name: 'Eagles', mascot: 'Swoop', colors: ['Midnight Green', 'Silver', 'Black'], division: 'nfc_east'},
        {id: 'washington_commanders', city: 'Washington', name: 'Commanders', mascot: 'Major Tuddy', colors: ['Burgundy', 'Gold'], division: 'nfc_east'},
        
        // NFC West
        {id: 'arizona_cardinals', city: 'Arizona', name: 'Cardinals', mascot: 'Big Red', colors: ['Cardinal Red', 'White', 'Black'], division: 'nfc_west'},
        {id: 'los_angeles_rams', city: 'Los Angeles', name: 'Rams', mascot: 'Rampage', colors: ['Royal Blue', 'Sol'], division: 'nfc_west'},
        {id: 'san_francisco_49ers', city: 'San Francisco', name: '49ers', mascot: 'Sourdough Sam', colors: ['Red', 'Gold'], division: 'nfc_west'},
        {id: 'seattle_seahawks', city: 'Seattle', name: 'Seahawks', mascot: 'Blitz', colors: ['College Navy', 'Action Green', 'Wolf Grey'], division: 'nfc_west'},
        
        // AFC North
        {id: 'baltimore_ravens', city: 'Baltimore', name: 'Ravens', mascot: 'Poe', colors: ['Purple', 'Black', 'Gold'], division: 'afc_north'},
        {id: 'cincinnati_bengals', city: 'Cincinnati', name: 'Bengals', mascot: 'Who Dey', colors: ['Black', 'Orange'], division: 'afc_north'},
        {id: 'cleveland_browns', city: 'Cleveland', name: 'Browns', mascot: 'Chomps', colors: ['Brown', 'Orange'], division: 'afc_north'},
        {id: 'pittsburgh_steelers', city: 'Pittsburgh', name: 'Steelers', mascot: 'Steely McBeam', colors: ['Black', 'Gold'], division: 'afc_north'},
        
        // AFC South
        {id: 'houston_texans', city: 'Houston', name: 'Texans', mascot: 'Toro', colors: ['Deep Steel Blue', 'Battle Red'], division: 'afc_south'},
        {id: 'indianapolis_colts', city: 'Indianapolis', name: 'Colts', mascot: 'Blue', colors: ['Royal Blue', 'White'], division: 'afc_south'},
        {id: 'jacksonville_jaguars', city: 'Jacksonville', name: 'Jaguars', mascot: 'Jaxson de Ville', colors: ['Teal', 'Black', 'Gold'], division: 'afc_south'},
        {id: 'tennessee_titans', city: 'Nashville', name: 'Titans', mascot: 'T-Rac', colors: ['Navy', 'Columbia Blue', 'Red'], division: 'afc_south'},
        
        // AFC East
        {id: 'buffalo_bills', city: 'Buffalo', name: 'Bills', mascot: 'Billy Buffalo', colors: ['Royal Blue', 'Red'], division: 'afc_east'},
        {id: 'miami_dolphins', city: 'Miami', name: 'Dolphins', mascot: 'T.D.', colors: ['Aqua', 'Orange'], division: 'afc_east'},
        {id: 'new_england_patriots', city: 'New England', name: 'Patriots', mascot: 'Pat Patriot', colors: ['Navy Blue', 'Red', 'Silver'], division: 'afc_east'},
        {id: 'new_york_jets', city: 'New York', name: 'Jets', mascot: null, colors: ['Gotham Green', 'Black'], division: 'afc_east'},
        
        // AFC West
        {id: 'denver_broncos', city: 'Denver', name: 'Broncos', mascot: 'Thunder', colors: ['Orange', 'Navy Blue'], division: 'afc_west'},
        {id: 'kansas_city_chiefs', city: 'Kansas City', name: 'Chiefs', mascot: 'KC Wolf', colors: ['Red', 'Gold'], division: 'afc_west'},
        {id: 'las_vegas_raiders', city: 'Las Vegas', name: 'Raiders', mascot: 'Raider Rusher', colors: ['Silver', 'Black'], division: 'afc_west'},
        {id: 'los_angeles_chargers', city: 'Los Angeles', name: 'Chargers', mascot: null, colors: ['Powder Blue', 'Gold', 'White'], division: 'afc_west'}
      ] AS team_data

      // Create Team nodes
      MERGE (t:Team {
        id: team_data.id,
        city: team_data.city,
        name: team_data.name,
        full_name: team_data.city + ' ' + team_data.name,
        colors: team_data.colors
      })
      ON CREATE SET
        t.mascot = team_data.mascot
        
      // Connect teams to their divisions
      WITH t, team_data
      MATCH (d:Division {division_id: team_data.division})
      MERGE (t)-[:PLAYS_IN]->(d);
    """
    self.db.run_query(query)

  def create_stadiums(self):
    query = """
      UNWIND [
        // NFC North
        {team: 'detroit_lions', name: 'Ford Field', city: 'Detroit', state: 'MI', roof: 'dome', capacity: 65000, surface: 'FieldTurf', opened: 2002},
        {team: 'chicago_bears', name: 'Soldier Field', city: 'Chicago', state: 'IL', roof: 'open', capacity: 61500, surface: 'Bermuda Grass', opened: 1924},
        {team: 'green_bay_packers', name: 'Lambeau Field', city: 'Green Bay', state: 'WI', roof: 'open', capacity: 81441, surface: 'Kentucky Bluegrass', opened: 1957},
        {team: 'minnesota_vikings', name: 'U.S. Bank Stadium', city: 'Minneapolis', state: 'MN', roof: 'fixed', capacity: 66655, surface: 'UBU Sports Speed S5-M', opened: 2016},
        
        // NFC South
        {team: 'atlanta_falcons', name: 'Mercedes-Benz Stadium', city: 'Atlanta', state: 'GA', roof: 'retractable', capacity: 71000, surface: 'FieldTurf', opened: 2017},
        {team: 'carolina_panthers', name: 'Bank of America Stadium', city: 'Charlotte', state: 'NC', roof: 'open', capacity: 75523, surface: 'Bermuda Grass', opened: 1996},
        {team: 'new_orleans_saints', name: 'Caesars Superdome', city: 'New Orleans', state: 'LA', roof: 'dome', capacity: 73208, surface: 'FieldTurf', opened: 1975},
        {team: 'tampa_bay_buccaneers', name: 'Raymond James Stadium', city: 'Tampa', state: 'FL', roof: 'open', capacity: 65618, surface: 'Bermuda Grass', opened: 1998},
        
        // NFC East
        {team: 'dallas_cowboys', name: 'AT&T Stadium', city: 'Arlington', state: 'TX', roof: 'retractable', capacity: 80000, surface: 'Hellas Matrix Turf', opened: 2009},
        {team: 'new_york_giants', name: 'MetLife Stadium', city: 'East Rutherford', state: 'NJ', roof: 'open', capacity: 82500, surface: 'FieldTurf', opened: 2010},
        {team: 'philadelphia_eagles', name: 'Lincoln Financial Field', city: 'Philadelphia', state: 'PA', roof: 'open', capacity: 69796, surface: 'Desso GrassMaster', opened: 2003},
        {team: 'washington_commanders', name: 'FedExField', city: 'Landover', state: 'MD', roof: 'open', capacity: 67617, surface: 'Bermuda Grass', opened: 1997},
        
        // NFC West
        {team: 'arizona_cardinals', name: 'State Farm Stadium', city: 'Glendale', state: 'AZ', roof: 'retractable', capacity: 63400, surface: 'Bermuda Grass', opened: 2006},
        {team: 'los_angeles_rams', name: 'SoFi Stadium', city: 'Inglewood', state: 'CA', roof: 'fixed', capacity: 70240, surface: 'Matrix Turf', opened: 2020},
        {team: 'san_francisco_49ers', name: "Levi's Stadium", city: 'Santa Clara', state: 'CA', roof: 'open', capacity: 68500, surface: 'Bermuda Grass', opened: 2014},
        {team: 'seattle_seahawks', name: 'Lumen Field', city: 'Seattle', state: 'WA', roof: 'partial', capacity: 69000, surface: 'FieldTurf Revolution 360', opened: 2002},
        
        // AFC North
        {team: 'baltimore_ravens', name: 'M&T Bank Stadium', city: 'Baltimore', state: 'MD', roof: 'open', capacity: 71008, surface: 'Bermuda Grass', opened: 1998},
        {team: 'cincinnati_bengals', name: 'Paycor Stadium', city: 'Cincinnati', state: 'OH', roof: 'open', capacity: 65515, surface: 'UBU Speed Series S5-M', opened: 2000},
        {team: 'cleveland_browns', name: 'FirstEnergy Stadium', city: 'Cleveland', state: 'OH', roof: 'open', capacity: 67895, surface: 'Kentucky Bluegrass', opened: 1999},
        {team: 'pittsburgh_steelers', name: 'Acrisure Stadium', city: 'Pittsburgh', state: 'PA', roof: 'open', capacity: 68400, surface: 'Kentucky Bluegrass', opened: 2001},
        
        // AFC South
        {team: 'houston_texans', name: 'NRG Stadium', city: 'Houston', state: 'TX', roof: 'retractable', capacity: 72220, surface: 'AstroTurf', opened: 2002},
        {team: 'indianapolis_colts', name: 'Lucas Oil Stadium', city: 'Indianapolis', state: 'IN', roof: 'retractable', capacity: 67000, surface: 'FieldTurf', opened: 2008},
        {team: 'jacksonville_jaguars', name: 'EverBank Stadium', city: 'Jacksonville', state: 'FL', roof: 'open', capacity: 67164, surface: 'Bermuda Grass', opened: 1995},
        {team: 'tennessee_titans', name: 'Nissan Stadium', city: 'Nashville', state: 'TN', roof: 'open', capacity: 69143, surface: 'Bermuda Grass', opened: 1999},
        
        // AFC East
        {team: 'buffalo_bills', name: 'Highmark Stadium', city: 'Orchard Park', state: 'NY', roof: 'open', capacity: 71608, surface: 'A-Turf Titan', opened: 1973},
        {team: 'miami_dolphins', name: 'Hard Rock Stadium', city: 'Miami Gardens', state: 'FL', roof: 'canopy', capacity: 65326, surface: 'Bermuda Grass', opened: 1987},
        {team: 'new_england_patriots', name: 'Gillette Stadium', city: 'Foxborough', state: 'MA', roof: 'open', capacity: 65878, surface: 'FieldTurf', opened: 2002},
        {team: 'new_york_jets', name: 'MetLife Stadium', city: 'East Rutherford', state: 'NJ', roof: 'open', capacity: 82500, surface: 'FieldTurf', opened: 2010},
        
        // AFC West
        {team: 'denver_broncos', name: 'Empower Field at Mile High', city: 'Denver', state: 'CO', roof: 'open', capacity: 76125, surface: 'Kentucky Bluegrass', opened: 2001},
        {team: 'kansas_city_chiefs', name: 'GEHA Field at Arrowhead Stadium', city: 'Kansas City', state: 'MO', roof: 'open', capacity: 76416, surface: 'Bermuda Grass', opened: 1972},
        {team: 'las_vegas_raiders', name: 'Allegiant Stadium', city: 'Las Vegas', state: 'NV', roof: 'dome', capacity: 65000, surface: 'Bermuda Grass', opened: 2020},
        {team: 'los_angeles_chargers', name: 'SoFi Stadium', city: 'Inglewood', state: 'CA', roof: 'fixed', capacity: 70240, surface: 'Matrix Turf', opened: 2020}
      ] AS stadium_data

      MERGE (s:Stadium {
        name: stadium_data.name,
        city: stadium_data.city,
        state: stadium_data.state,
        roof_type: stadium_data.roof,
        capacity: stadium_data.capacity, 
        surface: stadium_data.surface,
        opened: stadium_data.opened
      })     
    
      // Connect Stadium to Team
      WITH s, stadium_data
      MATCH (t:Team {id: stadium_data.team})
      MERGE (t)-[:PLAYS_AT]->(s);
    """
    self.db.run_query(query)