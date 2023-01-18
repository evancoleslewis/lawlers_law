import logging
import pandas as pd
import numpy as np
import requests 
import time
import re

from datetime import datetime, timedelta 
from bs4 import BeautifulSoup

season_dict = {'1996-11-01' : '1997-06-17'
              ,'1997-10-30' : '1998-06-15'
              ,'1999-11-02' : '2000-06-25'
              ,'2000-10-31' : '2001-06-15'
              ,'2001-10-30' : '2002-06-12'
              ,'2002-10-29' : '2003-06-15'
              ,'2003-10-28' : '2004-06-15'
              ,'2004-11-02' : '2005-06-23'
              ,'2005-11-01' : '2006-06-20'
              ,'2006-10-31' : '2007-06-14'
              ,'2007-10-30' : '2008-06-17'
              ,'2008-10-28' : '2009-06-14'
              ,'2009-10-27' : '2010-06-17'
              ,'2010-10-26' : '2011-06-12'
              ,'2011-12-25' : '2012-06-21'
              ,'2012-10-30' : '2013-06-20'
              ,'2013-10-29' : '2014-06-15'
              ,'2014-10-28' : '2015-06-16'
              ,'2015-10-27' : '2016-06-19'
              ,'2016-10-25' : '2017-06-12'
              ,'2017-10-17' : '2018-06-08'
              ,'2018-10-16' : '2019-06-13'
              ,'2019-10-22' : '2020-10-11'
              ,'2020-12-22' : '2021-07-20'
              ,'2021-10-19' : '2022-06-16'}

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

first_pbp_date = '1996-11-01'  # first game on bball reference that has play-by-play stats

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

def write_html_from_url(url : str):
    """
    Given url, retrieve html from url. Then write the html to file with abbreviated name.

    Return response code of url response.
    """

    resp_code = 0

    with requests.Session() as session:
        time.sleep(2)  # add delay to not overrun bball-ref with requests
        
        try:
            response = session.get(url)  # request contents of url
            resp_code = response.status_code  
            resp_html = response.text  # this is the html of the url    
            if resp_code == 200:  # status 200 means request was successful
                soup = BeautifulSoup(response.text, features='html.parser')

        except Exception as e:
            logging.info(f"The following error occurred when accessing {url} :")
            logging.info(f"{e}")

    return resp_code


def get_home_teams_on_date(date : datetime) -> list:
    """
    Given a date, get list of all home teams played on that date. Each home team represents a game on that date.
    
    Returns list of home teams. 
    """
    
    home_teams = []
    year, month, day = get_date_parts(date)  # split date parts for url formatting
    format_date = date.strftime("%Y%m%d")  # used for identifying hometeams in extract_home_teams()
    
    date_url = f"https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"
    date_soup, resp_code = get_soup(date_url)
    if resp_code == 200:
        home_teams = extract_home_teams(date_soup, format_date)
    
    return home_teams, resp_code


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


def get_all_games_on_date(game_date : datetime
                        ,home_teams : list) -> dict:
    """
    Given a date and list of home_teams return dictionary of all game_dicts on that date.
    
    Returns dictionary of game_dicts.
    """
    
    game_date_dict = dict()
    
    for home_team in home_teams:
        game_dict, resp_code = get_game_dict(game_date, home_team)  # get game_dict based on game_date, home_team
        
        if resp_code == 200:  # if resposne is successful, store data
            game_date_dict[home_team] = game_dict
        else:
            logging.info(f"    Error when getting {home_team} data on {game_date}")
            break
    
    return game_date_dict


def get_all_games_between_dates(start_game_date : str
                               ,end_game_date   : str) -> dict:
    """
    Given 2 dates, get list of all dates in between them (inclusive). Then get all games on those dates
    
    Returns dictionary of game_dicts.
    """
    
    logging.info(f"    Searching for game data in following date range: {start_game_date} - {end_game_date}\n")

    start_game_date = datetime.strptime(start_game_date, '%Y-%m-%d')  # ensure dates are formatted properly
    end_game_date = datetime.strptime(end_game_date, '%Y-%m-%d')
    day_delta = (end_game_date - start_game_date).days  # get number of days between both dates
    game_dates = [start_game_date + timedelta(days=i) for i in range(0, day_delta + 1)]  # get list of dates in between start and end dates
    
    all_games_dict = dict()

    for game_date in game_dates:
        game_date_str = game_date.strftime("%Y-%m-%d")

        home_teams, resp_code = get_home_teams_on_date(game_date)

        if resp_code == 200:  
            logging.info(f"    Home teams found on {game_date_str}: {home_teams}")
            all_games_dict[game_date_str] = get_all_games_on_date(game_date, home_teams).copy()  # else we get the game data and store it into all_games_dict
            logging.info(f"    Game data successfully retrieved\n")
        
        else:
            logging.info(f"    Issue occurred while getting games on: {game_date_str}")
            break

    return all_games_dict