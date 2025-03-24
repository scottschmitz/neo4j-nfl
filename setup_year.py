from datetime import timedelta

class NflSeasonYear:
  def __init__(self, db):
      self.db = db

  def create(self, season_year, season_start, regular_season_weeks, super_bowl_number):
    wild_card_week = season_start + timedelta(weeks = regular_season_weeks + 1)
    divisional_week = wild_card_week + timedelta(weeks = 1)

    # Add 3 days to get to the Sunday (Season starts on a Thursday)
    conference_championship_date = divisional_week + timedelta(weeks = 1, days=3)
    super_bowl_date = conference_championship_date + timedelta(weeks = 1)

    self.create_season(
      season_year, 
      season_start, 
      regular_season_weeks, 
      wild_card_week,
      divisional_week,
      conference_championship_date,  
      super_bowl_date,  
      super_bowl_number  
    )

  def create_season(
    self, 
    season_year, 
    season_start, 
    regular_season_weeks,
    wild_card_week,  
    divisional_weekend_start,  
    conference_championship_sunday,  
    super_bowl_date,  
    super_bowl_number  
  ):
    query = """
      // Create the [Season] node
      MERGE (s:Season {year: $season_year})
      ON CREATE SET 
        s.name = $season_year + ' NFL Season',
        s.start_date = date($season_start),
        s.end_date = date($super_bowl_date)

      // Create the [Week] nodes for the regular season
      WITH s
      UNWIND RANGE(1, $regular_season_weeks) AS week_num
      WITH  
        s,
        week_num, 
        DATE($season_start + DURATION({days: (week_num-1) * 7})) AS week_start,
        DATE($season_start + DURATION({days: (week_num-1) * 7 + 6})) AS week_end
      MERGE (w:Week {
        id: $season_year + '_week_' + toString(week_num),  
        season: $season_year,
        week_number: week_num,
        type: 'Regular Season',
        start_date: week_start,
        end_date: week_end
      })
      MERGE (s)-[:HAS_WEEK]->(w)

      // Create postseason weeks with calculated dates based on Super Bowl
      WITH s
      UNWIND [
        {
          num: $regular_season_weeks + 1, 
          name: 'Wild Card Round', 
          start: $wild_card_weekend_start, 
          end: DATE($wild_card_weekend_start + DURATION({days: 2}))
        },
        {
          num: $regular_season_weeks + 2,
          name: 'Divisional Round', 
          start: $divisional_weekend_start, 
          end: DATE($divisional_weekend_start + DURATION({days: 1}))
        },
        {
          num: $regular_season_weeks + 3,
          name: 'Conference Championships', 
          start: $conference_championship_sunday, 
          end: $conference_championship_sunday
        },
        {
          num: $regular_season_weeks + 4,
          name: 'Super Bowl ' + $super_bowl_number, 
          start: $super_bowl_date, 
          end: $super_bowl_date
        }
      ] AS playoff_week
      MERGE (w:Week {
        id: $season_year + '_week_' + playoff_week.num,  
        season: $season_year,  
        week_number: playoff_week.num,
        type: 'Postseason',
        name: playoff_week.name,
        start_date: playoff_week.start,
        end_date: playoff_week.end
      })
      MERGE (s)-[:HAS_WEEK]->(w)

      // Create ordered relationships between consecutive weeks
      WITH $season_year AS year
      MATCH (w1:Week {season: year})
      MATCH (w2:Week {season: year})
      WHERE w1.week_number = w2.week_number - 1
      MERGE (w1)-[:NEXT]->(w2)
    """
    
    # Convert dates to strings for Neo4j
    # wild_card_str = wild_card_week.strftime('%Y-%m-%d')
    # divisional_str = divisional_weekend_start.strftime('%Y-%m-%d')
    # championship_str = conference_championship_sunday.strftime('%Y-%m-%d')
    # super_bowl_str = super_bowl_date.strftime('%Y-%m-%d')
    # season_start_str = season_start.strftime('%Y-%m-%d')
    
    self.db.run_query(query, {
      "conference_championship_sunday": conference_championship_sunday,
      "divisional_weekend_start": divisional_weekend_start,  
      "regular_season_weeks": regular_season_weeks,  
      "season_start": season_start,
      "season_year": season_year,
      "super_bowl_date": super_bowl_date,
      "super_bowl_number": super_bowl_number,
      "wild_card_weekend_start": wild_card_week
    })
