import os
import pandas as pd
from datetime import datetime

def concat_all_csv(file_path):
    """
    Reads all csvs in the given file_path and concatenates them.
    Writes concatenated df to csv and creates a backup with timestamp.
    """

    all_csvs = [file for file in os.list_dir(file_path) if '.csv' in file]  # gets list of all csv names
    all_dfs = [pd.read_csv(file_path+file) for file in all_csvs]  # get list of all dataframes
    
    df_all_games = pd.concat(all_dfs)  # concat all dataframes into one
    df_all_games.drop_duplicates(inplace=True)  # remove any duplicate rows

    df_all_games.to_csv(file_path+'lawler.csv', index=False)  # write all games to csv
    df_all_games.to_csv(file_path+f'/backup/lawler_{str(datetime.now())}.csv', index=False)  # create backup based on current time

    return
