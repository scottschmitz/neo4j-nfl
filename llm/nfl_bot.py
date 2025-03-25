import os
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

# Get credentials from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")



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
You are tasked with reformatting a Cypher query result into a friendly, readable message. The original question and the Cypher result are provided to you. 
Your job is to present this information in a clear, concise manner without adding any additional data or performing any extra calculations. Do not use
any external knowledge beyond the information provided in the Cypher result.

Here is the original question that was asked:
<original_question>
{question}
</original_question>

Here is the Cypher query result:
<cypher_result>
{context}
</cypher_result>

To format your response:
1. Start by addressing the original question directly.
2. Present the information from the Cypher result in a natural, conversational tone.
3. Be concise. Limit yourself to 1-3 sentences.
4. Do not add any information that is not present in the Cypher result.
5. If the Cypher result is empty or doesn't provide a clear answer to the original question, state this clearly.
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