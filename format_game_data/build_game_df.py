import pandas as pd

def test_lawlers_law(score_list : list
                    ,win_team   : str
                    ,away_team  : str
                    ,home_team  : str) -> tuple:

    """
    Based on scores get lawler_bool, delta_at_100, score_at_100
    
    Returns lawler_bool, delta_at_100, score_at_100
    """
    
    high_score = 0  # initialize high_score for iteration
    i = -1  # initialize index
    while high_score < 100:
        i += 1
        score = score_list[i]
        away_score = int(score.split('-')[0])  # away_score precedes the dash
        home_score = int(score.split('-')[1])  # home_score succeeds the dash
        high_score = max([away_score, home_score])
    
    score_at_100 = score
    delta_at_100 = abs(away_score - home_score)
    
    if high_score == away_score:
        lawler_team = away_team
    else:
        lawler_team = home_team
    
    if lawler_team == win_team:
        lawler_bool = True
    else:
        lawler_bool = False
        
    return lawler_bool, delta_at_100, score_at_100


def get_game_attributes(away_team   : str
                        ,home_team  : str
                        ,score_list : list) -> tuple:
    """
    Based on teams & score_list, get winner, loser, reached_100_bool, lawler_bool, score_at_100, final_score
    """
    
    # get final scores
    final_score = score_list[-1]  # final_score is last in score_list
    away_score = int(final_score.split('-')[0])  # away_score precedes the dash
    home_score = int(final_score.split('-')[1])  # home_score succeeds the dash
    
    # get winner loser
    if away_score > home_score:
        win_team = away_team
        lose_team = home_team
    else:
        win_team = home_team
        lose_team = away_team
        
    # get 100s
    reached_100_bool = (max(away_score, home_score) >= 100)  # if one or both teams reached 100 return True else False
    lawler_bool = None
    delta_at_100 = None
    score_at_100 = None
    
    if reached_100_bool:  # if someone reached 100, test lawlers
        lawler_bool, delta_at_100, score_at_100 = test_lawlers_law(score_list, win_team, away_team, home_team)
    
    
    return final_score, win_team, lose_team, reached_100_bool, lawler_bool, delta_at_100, score_at_100


def build_all_games_df(all_games_dict : dict) -> pd.DataFrame:
    """
    Builds dataframe based on home_team, away_team, score_list.
    
    Returns game_df.
    """
    
    df_dict = dict()  # dictionary where all dataframes will be stored

    for game_date in all_games_dict.keys():  # iterate through each day
        game_day_dict = all_games_dict[game_date]
        
        for home_team in game_day_dict.keys():  # each day has a set of home_team(s)
            game_dict = game_day_dict[home_team]  # each home_team represents a game on that day
            away_team = game_dict['away_team']
            home_team = game_dict['home_team']
            score_list = game_dict['score_list']
            
            
            final_score = None
            win_team = None
            lose_team = None
            reached_100_bool = None
            lawler_bool = None 
            delta_at_100 = None 
            score_at_100 = None 

            if len(score_list) > 0:  # if we were able to get a score_list, we overwrite the attributes initialized above
                final_score, win_team, lose_team, reached_100_bool, lawler_bool, delta_at_100, score_at_100 = get_game_attributes(away_team, home_team, score_list)
            
            game_df = pd.DataFrame({'game_date': [game_date]
                                ,'away_team' : [away_team]
                                ,'home_team' : [home_team]
                                ,'final_score' : [final_score]
                                ,'win_team' : [win_team]
                                ,'lose_team' : [lose_team]
                                ,'reached_100_bool' : [reached_100_bool]
                                ,'lawler_bool' : [lawler_bool]
                                ,'score_at_100' : [score_at_100]
                                ,'delta_at_100' : [delta_at_100]})

            df_dict[game_date+'_'+home_team] = game_df.copy()  # each df has a unique game_date + home_team pairing
        
    all_games_df = pd.concat(df_dict).reset_index(drop=True)

    return all_games_df