import sys
import logging 
import time
from datetime import datetime, timedelta

from extract.extract_game_data import get_game_html_between_dates
from transform.build_game_df import read_game_data_from_html 

def main(start_game_date : str
        ,end_game_date   : str):
    
    start = datetime.now()
    logging.basicConfig(filename='log/lawler.log', level=logging.INFO, format='%(message)s')
    logging.info(f"***Started run at {start}\n")

    all_html_dict = get_game_html_between_dates(start_game_date, end_game_date)  # write the html between dates

    all_games_df = read_game_data_from_html(all_html_dict)  # read the data from the html files
    
    # TODO: build load function to concat all resulting dataframes into 1, eventually load into database
    
    if all_games_df.shape[0] > 0:  # if df is non-empty, write it to csv
        all_games_df.to_csv(f'data/csv/lawler_{start_game_date}_{end_game_date}.csv', index=False)
    
    logging.info(f"***Completed run in {datetime.now() - start}\n")

    return

if __name__ == "__main__":

    try:
        start_game_date = sys.argv[1]  # first date input (if one was given)
    except:
        start_game_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # if no input is given, take yesterday as default

    try:
        end_game_date = sys.argv[2]  # second date input (if one was given)
    except:
        end_game_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # if no input is given, take yesterday as default

    main(start_game_date, end_game_date)  # call the main function with given date range