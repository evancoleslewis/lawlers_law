import logging
import pandas as pd
import numpy as np
import requests 
import time
import re

from datetime import datetime, timedelta 
from bs4 import BeautifulSoup

team_dict = {'ATL' : ["Atlanta Hawks"]
            ,'BUF' : ["Buffalo Braves"]
            ,'BKN' : ["Brooklyn Nets"]
            ,'BOS' : ["Boston Celtics"]
            ,'BUF' : ['Buffalo Braves']
            ,'CHA' : ["Charlotte Hornets"]
            ,'CHH' : ['Charlotte Hornets']
            ,'CHI' : ["Chicago Bulls"]
            ,'CLE' : ["Cleveland Cavaliers"]
            ,'DAL' : ["Dallas Mavericks"]
            ,'DEN' : ["Denver Nuggets"]
            ,'DET' : ["Detroit Pistons"]
            ,'GSW' : ["Golden State Warriors"]
            ,'HOU' : ["Houston Rockets"]
            ,'IND' : ["Indiana Pacers"]
            ,'KCK' : ['Kansas City Kings']
            ,'LAC' : ["Los Angeles Clippers"]
            ,'LAL' : ["Los Angeles Lakers"]
            ,'MEM' : ["Memphis Grizzlies"]
            ,'MIA' : ["Miami Heat"]
            ,'MIL' : ["Milwaukee Bucks"]
            ,'MIN' : ["Minnesota Timberwolves"]
            ,'NJN' : ['New Jersey Nets']
            ,'NOJ' : ['New Orleans Jazz']
            ,'NOP' : ["New Orleans Pelicans"]
            ,'NYK' : ["New York Knicks"]
            ,'OKC' : ["Oklahoma City Thunder"]
            ,'ORL' : ["Orlando Magic"]
            ,'PHI' : ["Philadelphia 76ers"]
            ,'PHX' : ["Phoenix Suns"]
            ,'PHO' : ["Phoenix Suns"]  # b-ball ref seems to use both?
            ,'POR' : ["Portland Trail Blazers"]
            ,'SAC' : ["Sacramento Kings"]
            ,'SAS' : ["San Antonio Spurs"]
            ,'SEA' : ["Seattle SuperSonics"]
            ,'TOR' : ["Toronto Raptors"]
            ,'UTA' : ["Utah Jazz"]
            ,'WAS' : ["Washington Wizards"]
            ,'WSB' : ['Washington Bullets']
            }

### functions below are for parsing html ###

def get_soup(file_name : str
            ,html      : str):
    """
    Given html, get bs4 parsed html AKA soup.
    Return soup of html.
    """

    soup = BeautifulSoup('')

    try:
        soup = BeautifulSoup(response.text, features='html.parser')

    except Exception as e:
        logging.info(f"The following error occurred when accessing {file_name} :")
        logging.info(f"{e}")

    return soup

def get_away_team(game_soup
                 ,home_team : str) -> str:
    """
    Given home_team and game_soup, extract away team of game.
    
    Returns away team.
    """
    
    meta_tags = game_soup.find_all('meta')
    pattern = re.compile(f"(.*)content=\"(.*) vs {home_team}")

    away_team = None
    i = -1

    # search for away_team, if team is not found within meta_tags, return 'not_found'
    while not away_team:
        i += 1  # move to next index
        if i == len(meta_tags): away_team = 'not_found'  # if index out of bounds, we could not find team

        tag = meta_tags[i]
        if pattern.match(str(tag)):
            team_str = re.search(f"content=\"(.*) vs {home_team}", str(tag)).group(1)  # away team is beginning of this string
            away_team = team_str[:3]  # first 3 characters will be away team
            
    return away_team


def get_score_list(game_soup) -> list:
    """
    Given table of bs4.element.tag's, extract score from each tag.
    
    Returns list of unique scores in chronological order.
    """
    
    score_tags = game_soup.find_all('td', class_='center')
    score_pattern = re.compile("[0-9](.*)[0-9]")  # pattern for what scores look like
    
    scores = []
    for tag in score_tags:
        score = re.search(">(.*)<", str(tag)).group(1)  # all scores are formatted as >away_score-home_score<
        if score not in scores: scores.append(score)
        
    scores = [score for score in scores if score_pattern.match(score)]
    
    return scores

def get_game_dict(game_date : datetime
                 ,home_team : str) -> dict:
    """
    Given home_team and date, contructs dictionary of home team, away team, ordered list of scores.
    
    Returns dictionary of teams, score_list (formatted HOME-AWAY)
    """
    
    format_date = game_date.strftime("%Y%m%d")  # url reads date without dashes
    
    pbp_url = f"https://www.basketball-reference.com/boxscores/pbp/{format_date}0{home_team}.html"  # play-by-play (pbp) will have scores
    game_soup, resp_code = get_soup(pbp_url)
    
    away_team = None 
    score_list = None 

    if resp_code == 200:  # if a play-by-play page is found, get scores and away_team
        away_team = get_away_team(game_soup, home_team)  
        score_list = get_score_list(game_soup)
    
    
    game_dict = {'away_team'  : away_team
                ,'home_team'  : home_team
                ,'score_list' : score_list}
    
    return game_dict, resp_code

### functions below are for when data is extracted from html ###

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
        
    all_games_df = pd.DataFrame()  # in case there is no game data in the date range
    
    if df_dict:  # if dict is not empty, concat into a dataframe
        all_games_df = pd.concat(df_dict).reset_index(drop=True)

    return all_games_df