import os
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama

from dotenv import load_dotenv
load_dotenv()

llm = ChatOllama(model="llama3.2")

# Load environment variables from .env
load_dotenv()

# Get credentials from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USER,
    password=NEO4J_PASSWORD
)

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about the NFL.
Convert the user's question based on the schema.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

If no data is returned, do not attempt to answer the question.
Only respond to questions that require you to construct a Cypher statement.
Do not include any explanations or apologies in your responses.

Overview of the Schema:
A Player plays for a Team if they have a relationship of PLAYS_FOR to the Team.
A Team played in a Game if they have a relationship of WAS_HOME or WAS_AWAY to the Game.
Out of the 2 teams that played in a Game, one team will have a relationship of WAS_HOME and the other will have a relationship of WAS_AWAY. Whoever scored
more points won the game.

When searching for a team make sure to always search by its id. The following are the valid ids for the Teams:
'buffalo_bills',
'miami_dolphins'
'new_york_jets'
'new_england_patriots'
'baltimore_ravens'
'cincinnati_bengals'
'cleveland_browns'
'pittsburgh_steelers'
'houston_texans'
'indianapolis_colts'
'jacksonville_jaguars'
'tennessee_titans'
'denver_broncos'
'kansas_city_chiefs'
'las_vegas_raiders'
'los_angeles_chargers'
'dallas_cowboys'
'new_york_giants'
'philadelphia_eagles'
'washington_commanders'
'chicago_bears'
'detroit_lions'
'green_bay_packers'
'minnesota_vikings'
'atlanta_falcons'
'carolina_panthers'
'new_orleans_saints'
'tampa_bay_buccaneers'
'arizona_cardinals'
'los_angeles_rams'
'san_francisco_49ers'
'seattle_seahawks'

Examples: 

Get Players and their Positions for the Lions:
MATCH (p:Player)-[:PLAYS_FOR]->(lions:Team {{id: 'detroit_lions'}})
MATCH (p)-[:PLAYS]->(pos:Position)
RETURN p, pos

Who plays for QB for the Dallas Cowboys?
MATCH (p:Player)-[:PLAYS_FOR]->(cowboys:Team {{id: 'dallas_cowboys'}})
MATCH (p)-[:PLAYS]->(pos:Position {{name: 'QB'}})
RETURN p

Which colleges did players for the Cardinals attend?
MATCH (t:Team {{id: 'arizona_cardinals'}})-[:PLAYS_FOR]-(p:Player)-[:ATTENDED]->(c:College)
RETURN t, p, c

What stadiums did the Packers play in?
// Match away games where the Packers were the away team
MATCH (t:Team {{id: 'green_bay_packers'}})-[:WAS_AWAY]-(awayGame:Game)-[:PLAYED_AT]->(awayStadium:Stadium)
WITH awayStadium AS Stadium
RETURN DISTINCT Stadium
UNION
// Match home games where the Packers were the home team
MATCH (t:Team {{id: 'green_bay_packers'}})-[:WAS_HOME]-(homeGame:Game)-[:PLAYED_AT]->(homeStadium:Stadium)
WITH homeStadium AS Stadium
RETURN DISTINCT Stadium;

Determine if having a home stadium in a dome affects performance when playing away in open air
MATCH (domeTeam:Team)-[:PLAYS_AT]->(dome:Stadium {{roof_type: 'dome'}})
MATCH (domeTeam)-[awayRel:WAS_AWAY]->(awayGame:Game)
MATCH (homeTeam:Team)-[homeRel:WAS_HOME]->(awayGame)
MATCH (awayGame)-[:PLAYED_AT]->(awayStadium {{roof_type: 'open'}})
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

Schema: {schema}
Question: {question}
"""

RESPONSE_TEMPLATE = """
Given the following Cypher query results, assume that the results are correct and are 
related to the query. If the query is asking about movies, and it is a list of movies,
then assume the list is correct. Provide the response in an easy to read sentence or two.

Results: {context}

Respond with only the results exactly as they appear above, with no additional text or explanations.
"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"],
)

response_prompt = PromptTemplate(
    template=RESPONSE_TEMPLATE,
    input_variables=["context"],
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    qa_prompt=response_prompt,
    validate_cypher=True,
    verbose=True,
    allow_dangerous_requests=True
)

def run_cypher(q):
    return cypher_chain.invoke({"query": q})['result']

while (q := input("> ")) != "exit":
    print(run_cypher(q))