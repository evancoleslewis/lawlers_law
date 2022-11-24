from extract_game_data.extract_game_data import get_all_games_on_date
from format_game_data.build_game_df import build_game_df
import pandas as pd

def main():
    
    # TODO: Set to yesterday
    game_date = '2022-11-22'

    game_date_dict = get_all_games_on_date(game_date)
    
    # TODO: clean up dataframe concatenation
    game_dict = game_date_dict[game_date]
    df_dict = dict()
    for home_team in game_dict.keys():
        game_df = build_game_df(game_dict[home_team])
        df_dict[home_team] = game_df.copy()
    
    all_games_df = pd.concat(df_dict).reset_index(drop=True)
    
    # TODO: write data to csv (eventually to database)
    all_games_df.to_csv(f'temp_csvs/lawler_{game_date}.csv', index=False)
    
    return

main()