import os
import pandas as pd
from datetime import datetime

def concat_all_csv(file_path : str
                    ,all_csvs : list) -> list:

    """
    Reads all csv file names into dataframes. 
    
    Returns all dataframes concatenated into one dataframe.
    """

    df_dict = dict()

    for csv in all_csvs:
        try:
            df = pd.read_csv(file_path+csv)
            df_dict[csv] = df.copy()
        except:
            print(f"Unable to read {csv}")
        
    all_games_df = pd.concat(df_dict).reset_index(drop=True)  # concat all into 1 df
    all_games_df.drop_duplicates(inplace=True)  # remove any duplicate rows

    return all_games_df


def write_all_csv(file_path):
    """
    Reads all csvs in the given file_path and concatenates them.
    Writes concatenated df to csv and creates a backup with timestamp.
    """
    
    all_csvs = [file for file in os.listdir(file_path) if '.csv' in file]  # gets list of all csv names
    all_games_df = concat_all_csv(file_path, all_csvs)  # read and concat all csvs

    all_games_df.to_csv(file_path+'lawler.csv', index=False)  # write all games to csv
    all_games_df.to_csv(file_path+f'backup/lawler_{str(datetime.now())}.csv', index=False)  # create backup based on current time

    return

# csv_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data/csv/'))  # get cwd, go one level up, and join data/csv to get full path
# write_all_csv(csv_file_path+'/')  # run function with csv_file_path