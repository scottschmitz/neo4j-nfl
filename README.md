# 2024 NFL Team Info

![alt text](./docs/schema_visualization.png)

## Running the Docker Image
```
docker compose up -d
```

## Setup the Environment (.env)
Create a `.env` file at the root of the project. This project is setup to use a [Google Gemini API key which you can generate here.](https://ai.google.dev/gemini-api/docs/api-key) Your `.env` file should look something like below.
```
NEO4J_URI=neo4j://localhost
NEO4J_USER=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD
GEMINI_API_KEY=YOU_API_KEY
```

## Asking Questions
```
cd llm
python -m venv neo4f-nfl-llm
source neo4j-nfl-llm/bin/activate

pip install -r requirements.txt

python nfl_bot.py
```

After running the command you may begin asking question such as
```
> Who did the Bears draft in 2024?
The Bears drafted Austin Booker, Tory Taylor, Kiran Amegadjie, Rome Odunze, and Caleb Williams in 2024.
> What schools did the Saints draft from in 2023?
In 2023, the Saints drafted players from Wake Forest, Minnesota, Fresno St., Old Dominion, TCU, Notre Dame, and Clemson.
> Who plays RB for the 49ers?
Ke'Shawn Vaughn, Patrick Taylor, Christian McCaffrey, Jordan Mason, and Isaac Guerendo play RB for the 49ers.
> what was the most popular school to draft from in 2024?
In 2024, the most popular school to draft from was Michigan.  They had 13 players drafted.
> what was the most popular school to draft from across all the years?
The most popular school to draft from across all years was Michigan.  They had 22 players drafted.
> what are the top 5 schools to get players drafted?
The top 5 schools that have had players drafted are: Michigan (22 players), Alabama (20), Georgia (18), Texas (16), and Penn St. (14).
```
To view the generated Cypher Query with results in the output simply update `verbose=False,` to `True`.

## Importing Data

### Create a venv
```
cd importer
python -m venv neo4f-nfl
source neo4j-nfl/bin/activate

pip install -r requirements.txt
```

### Call the importer
```
python importer.py 
```

### View in neo4j
1. Connect to your instance (defaults to http://localhost:7474/browser/)
1. Run some queries!


## Example Queries

### Get the metadata
```
CALL db.schema.visualization();
```

### Get all data
```
MATCH (n) RETURN n;
```

### Get the Positions for Players on a Team
```
MATCH (p:Player)-[:PLAYS_FOR]->(lions:Team {id: 'detroit_lions'})
MATCH (p)-[:PLAYS]->(pos:Position)
RETURN p, pos
```

### What College has the most pro QBs?
```
MATCH (c:College)-[:ATTENDED]-(p:Player)-[:PLAYS]->(pos:Position {name: 'QB'})
WITH pos, c, COUNT(p) as PlayerCount
ORDER BY PlayerCount DESC
RETURN pos.name, c.name, PlayerCount
LIMIT 5;
```

### Get all players from Alabama on either the Packers or Lions
```
MATCH (lions:Team {id: 'detroit_lions'})<-[:PLAYS_FOR]-(lionsPlayer:Player)
MATCH (lionsPlayer)-[:ATTENDED]->(college:College {name: 'Alabama'})
MATCH (college)<-[:ATTENDED]-(packersPlayer:Player)
MATCH (packersPlayer)-[:PLAYS_FOR]->(packers:Team {id: 'green_bay_packers'})
RETURN lionsPlayer, packersPlayer, college, lions, packers;
```

### Identify Most Popular College for a Team
```
MATCH (t:Team)-[:PLAYS_FOR]-(p:Player)-[:ATTENDED]->(c:College)
WITH t, c, COUNT(p) AS player_count
ORDER BY player_count DESC
WITH t, COLLECT({college: c.name, count: player_count}) AS colleges
RETURN t.name AS team, HEAD(colleges).college AS top_college, HEAD(colleges).count AS player_count;
```

### Identify Most Popular College for a Team
```
MATCH (t:Team)-[:PLAYS_FOR]-(p:Player)-[:ATTENDED]->(c:College)
WITH t, c, COUNT(p) AS player_count
ORDER BY player_count DESC
WITH t, COLLECT({college: c, count: player_count}) AS colleges
WITH t, HEAD(colleges) AS top_college
MATCH (c:College {name: top_college.college.name})
MERGE (t)-[f:FAVORS]->(c)
SET f.count = top_college.count
RETURN t, c, f;
```

### Identify Most Popular College for a Division
```
MATCH (d:Division)<-[:PLAYS_IN]-(t:Team)-[:PLAYS_FOR]-(p:Player)-[:ATTENDED]->(c:College)
WITH d, c, COUNT(p) AS player_count
ORDER BY player_count DESC
WITH d, COLLECT({college: c, count: player_count}) AS colleges
WITH d, HEAD(colleges) AS top_college
MATCH (c:College {name: top_college.college.name})
MERGE (d)-[f:FAVORS]->(c)
SET f.count = top_college.count
RETURN d, c, f;
```

### Do Dome Teams Win in 'Open' Stadiums?
```
MATCH (domeTeam:Team)-[:PLAYS_AT]->(dome:Stadium {roof_type: 'dome'})
MATCH (domeTeam)-[awayRel:WAS_AWAY]->(awayGame:Game)
MATCH (homeTeam:Team)-[homeRel:WAS_HOME]->(awayGame)
MATCH (awayGame)-[:PLAYED_AT]->(awayStadium {roof_type: 'open'})
WITH domeTeam, awayGame, homeTeam, awayRel.score AS awayScore, homeRel.score AS homeScore
ORDER BY awayGame.date ASC
RETURN 
  awayGame.date, 
  homeTeam.name as HomeTeam, 
  domeTeam.name as DomeTeam, 
  awayScore > homeScore as DomeTeamWonInOpenAir,
  CASE 
    WHEN awayScore > homeScore THEN domeTeam.name
    WHEN homeScore > awayScore THEN homeTeam.name
    ELSE 'Tie Game'
  END AS Winner;
```


## Downloading New Data
This is currently pulling data from Pro Football Reference which has a rate limit of no more than 20 requests per minute. This downloader should remain within these boundaries aiming for 16 per minute. All data for the 2024 season is already available via the `rawdata` folder. To get other seasons, update `download_season.py` with the appropriate year. Note that there are currently a number of bugs that will require manually correcting the results.
1. Playoff weeks are non-numerical and must be replaced with the week number.
1. The `games.csv` files will be missing headers and must be updated to be `Week,Day,Date,Time,,Win/Loss,OT,Rec,Location,Opp,ScoreTm,ScoreOpp,1stD,TotYd,PassY,RushY,TO,1stD,TotYd,PassY,RushY,TO,Offense,Defense,Sp. Tms`