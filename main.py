from extract_game_data.extract_game_data import get_all_games_on_date
from format_game_data.build_game_df import build_all_games_df
import pandas as pd
from datetime import datetime, timedelta

def main():
    
    game_date = (datetime.today() - timedelta(days=1))  # get yesterday's date
    all_games_dict = get_all_games_on_date(game_date)  # get all games from yesterday
    all_games_df = build_all_games_df(all_games_dict)  # format data into dataframe

    # TODO: write data to csv (eventually to database)
    all_games_df.to_csv(f'csv/lawler_{game_date.strftime("%Y-%m-%d")}.csv', index=False)  # write data to csv
    
    return

main()