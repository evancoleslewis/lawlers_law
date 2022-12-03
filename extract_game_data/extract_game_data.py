import pandas as pd
import numpy as np
import requests 
import time
import re

from datetime import datetime, timedelta 
from bs4 import BeautifulSoup

team_dict = {'ATL' : ["Atlanta Hawks"]
            ,'BKN' : ["Brooklyn Nets"]
            ,'BOS' : ["Boston Celtics"]
            ,'CHA' : ["Charlotte Hornets"]
            ,'CHI' : ["Chicago Bulls"]
            ,'CLE' : ["Cleveland Cavaliers"]
            ,'DAL' : ["Dallas Mavericks"]
            ,'DEN' : ["Denver Nuggets"]
            ,'DET' : ["Detroit Pistons"]
            ,'GSW' : ["Golden State Warriors"]
            ,'HOU' : ["Houston Rockets"]
            ,'IND' : ["Indiana Pacers"]
            ,'LAC' : ["Los Angeles Clippers"]
            ,'LAL' : ["Los Angeles Lakers"]
            ,'MEM' : ["Memphis Grizzlies"]
            ,'MIA' : ["Miami Heat"]
            ,'MIL' : ["Milwaukee Bucks"]
            ,'MIN' : ["Minnesota Timberwolves"]
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
            ,'TOR' : ["Toronto Raptors"]
            ,'UTA' : ["Utah Jazz"]
            ,'WAS' : ["Washington Wizards"] }

def get_date_parts(date : datetime) -> tuple:
    
    """
    Given a date, returns year,month,day as strings. 
    
    If any date part is less than 10, add leading '0'.
    """
    
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    
    if date.month < 10 : month = '0' + month
    if date.day < 10 : day = '0' + day
    
    return year, month, day

def get_soup(url : str):
    """
    Given url, get bs4 parsed html AKA soup.

    Return soup of url.
    """

    with requests.Session() as session:
        time.sleep(5)  # add delay to not overrun bball-ref with requests
        response = session.get(url)  # request contents of url
        if response.status_code == 200:  # status 200 means request was successful
            soup = BeautifulSoup(response.text, features='html.parser')
        else:
            print(f'Unable to get data from: {url}')
            soup = None

    

    return soup


def get_home_teams_on_date(date : datetime) -> list:
    """
    Given a date, get list of all home teams played on that date.
    
    Returns list of home teams. 
    """
    
    year, month, day = get_date_parts(date)  # split date parts for url formatting
    format_date = date.strftime("%Y%m%d")  # used for identifying hometeams in extract_home_teams()
    print(f"Attempting to find home teams on {date.strftime('%Y-%m-%d')}")
    
    date_url = f"https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"
    date_soup = get_soup(date_url)
    home_teams = extract_home_teams(date_soup, format_date)
    
    return home_teams


def extract_home_teams(date_soup, format_date) -> list:
    """
    Extracts home teams from bs4 element.
    
    Returns home team.
    """
    
    a_elements = date_soup.find_all('a')

    box_scores = [bs for bs in a_elements if f'/boxscores/{format_date}' in str(bs)]  # get all box_score elements
    home_teams = [str(bs).split('.html')[0][-3:] for bs in box_scores]  # each home team appears in 3 letter abbrev before ".html"
    clean_home_teams = set([team for team in home_teams if team in team_dict.keys()]) # verify teams are in dict, get unique set of teams
    
    return list(clean_home_teams)


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
    
    game_url = f"https://www.basketball-reference.com/boxscores/pbp/{format_date}0{home_team}.html"
    game_soup = get_soup(game_url)

    away_team = get_away_team(game_soup, home_team)  # extract away team
    scores = get_score_list(game_soup)
    
    
    game_dict = {'away_team'  : away_team
                ,'home_team'  : home_team
                ,'score_list' : scores}
    
    return game_dict


def get_all_games_on_date(game_date : datetime) -> dict:
    """
    Given a date return dictionary of all game_dicts on that date.
    
    Returns dictionary of game_dicts.
    """
    
    home_teams = get_home_teams_on_date(game_date)
    
    game_dict = dict()
    all_games_dict = dict()
    
    for home_team in home_teams:
        game_dict[home_team] = get_game_dict(game_date, home_team)
    
    game_date_str = game_date.strftime("%Y-%m-%d")
    all_games_dict[game_date_str] = game_dict
    print(f"Successfully Retrieved data for games on {game_date_str}")

    return all_games_dict


def get_all_games_between_dates(start_game_date : str
                               ,end_game_date   : str) -> dict:
    """
    Given 2 dates, geta list of all dates in between them (inclusive). Then get all games on those dates
    
    Returns dictionary of game_dicts.
    """
    
    start_game_date = datetime.strptime(start_game_date, '%Y-%m-%d')  # ensure dates are formatted properly
    end_game_date = datetime.strptime(end_game_date, '%Y-%m-%d')
    day_delta = (end_game_date - start_game_date).days  # get number of days between both dates
    game_dates = [start_game_date + timedelta(days=i) for i in range(0, day_delta + 1)]  # get list of dates in between start and end dates
    
    all_games_dict = dict()

    for game_date in game_dates:
        try:
            game_date_str = game_date.strftime("%Y-%m-%d")
            all_games_dict[game_date_str] = get_all_games_on_date(game_date)[game_date_str]
        except:
            print(f"No game found on {game_date_str}")
        
    return all_games_dict