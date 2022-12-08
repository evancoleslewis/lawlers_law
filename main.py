import sys
from datetime import datetime, timedelta
from extract_game_data.extract_game_data import get_all_games_between_dates
from format_game_data.build_game_df import build_all_games_df

def main(start_game_date : str
        ,end_game_date   : str):
    
    all_games_dict = get_all_games_between_dates(start_game_date, end_game_date)
    all_games_df = build_all_games_df(all_games_dict)
    
    # TODO: build load function to concat all resulting dataframes into 1, eventually load into database
    all_games_df.to_csv(f'csv/lawler_{start_game_date}_{end_game_date}.csv', index=False)
    
    return

try:
    start_game_date = sys.argv[1]  # first date input (if one was given)
except:
    start_game_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # if no input is given, take yesterday as default

try:
    end_game_date = sys.argv[2]  # second date input (if one was given)
except:
    end_game_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # if no input is given, take yesterday as default

main(start_game_date, end_game_date)  # call the main function with given date range