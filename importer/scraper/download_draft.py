from meta_data import team_abbrs, team_abbr_to_id
from pro_football_reference_parser import make_soup, make_csv

year = 2023

draft_url = f"https://www.pro-football-reference.com/years/{year}/draft.htm"
output_dir = f'rawdata/{year}/draft/'

draft_soup = make_soup(draft_url)
make_csv(draft_soup, 'drafts', f"{output_dir}/draft.csv")
