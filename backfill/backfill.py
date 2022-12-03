import sys
sys.path.insert(1 , '/Users/evan.lewis/github/lawlers_law')

from datetime import datetime, timedelta
from extract_game_data.extract_game_data import get_all_games_between_dates
from format_game_data.build_game_df import build_all_games_df

def main():
    
    start_game_date = '2022-11-29'  # starting here
    end_game_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    all_games_dict = get_all_games_between_dates(start_game_date, end_game_date)
    all_games_df = build_all_games_df(all_games_dict)
    
    # TODO: write data to csv (eventually to database)
    all_games_df.to_csv(f'csv/lawler_{start_game_date}_{end_game_date}.csv', index=False)
    
    return

main()