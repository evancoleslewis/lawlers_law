import logging
import pandas as pd
import numpy as np
import requests 
import time
import re
import os

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

def get_soup(html : str):
    """
    Given html, get bs4 parsed html AKA soup.
    Return soup of html.
    """

    try:
        soup = BeautifulSoup(html, features='html.parser')

    except Exception as e:
        logging.info(f"The following error occurred when getting soup:\n{e}")

    return soup

def abbrev_url_to_file_name(url : str) -> str:
    """
    Abbreviate the given url to be suitable for a file name. (remove commonalities/illegal characters)

    Return cleaned abbrevation of url.
    """

    # define illegal characters and their replacements
    replace_dict = {'?'  : ''
                    ,'&' : ''
                    ,'=' : ''
                    ,'/' : '_'
                    }

    url_tail = url.split('boxscores/')[-1]  # get the last piece of the url (unique for each date/game)
    
    for ill in replace_dict.keys():
        url_tail = url_tail.replace(ill, replace_dict[ill])  # replace each illegal character
    
    return url_tail

def get_full_file_path(file_name : str
                      ,date      : datetime) -> str:
    """
    Given file_name and date, ensure correct directory exists: lawlers_law/data/html/{date}/

    Returns full_file_path of corresponding directory.
    """

    script_path = os.path.dirname(__file__)  # get directory of this script
    file_path = os.path.join(script_path, f"../data/html/{date.strftime('%Y-%m-%d')}/")  # use script_path to access lawlers_law/data/html directory
    file_path = os.path.abspath(os.path.realpath(file_path))  # ensure file path is readable (changes /extract/../data to /lawlers/data/)

    # ensure file path exists
    if not os.path.exists(file_path):
        os.makedirs(file_path)  # if not exists, create it
        logging.info(f"New directory created: {file_path}")

    full_file_path = file_path + '/' + file_name  # add file_name to get full_file_path

    return full_file_path


def extract_home_teams(date_html : str
                    ,game_date : str) -> list:
    """
    Gets soup from html and parses soup to get list of home_teams.
    
    Returns list of home team.
    """
    
    format_date = game_date.strftime("%Y%m%d")
    
    date_soup = get_soup(date_html)  # turn html to readable soup

    a_elements = date_soup.find_all('a')
    box_scores = [bs for bs in a_elements if f'/boxscores/{format_date}' in str(bs)]  # get all box_score elements
    home_teams = [str(bs).split('.html')[0][-3:] for bs in box_scores]  # each home team appears in 3 letter abbrev before ".html"
    clean_home_teams = set([team for team in home_teams if team in team_dict.keys()]) # verify teams are in dict, get unique set of teams
    
    return list(clean_home_teams)


def get_date_range(start_game_date : str
                  ,end_game_date   : str) -> list:
    """
    Takes start date and end date and does 2 things:
        1. Ensure dates are formatted properly
        2. Generates a list of dates in between start and end (inclusive)
    
    Returns formatted date_list
    """

    try:
        start_game_date = datetime.strptime(start_game_date, '%Y-%m-%d')  # ensure dates are formatted properly
        end_game_date = datetime.strptime(end_game_date, '%Y-%m-%d')
        day_delta = (end_game_date - start_game_date).days  # get number of days between both dates
        game_dates = [start_game_date + timedelta(days=i) for i in range(0, day_delta + 1)]  # get list of dates in between start and end dates
    
    except Exception as e:
        print('There is something wrong with the dates inputted. Ensure your dates formatted as YYYY-MM-DD.')
        logging.error(f"The following error occurred when trying to generate a date range:\n{e}")

    return game_dates 

def write_html(url     : str 
               ,abbrev : str
               ,date   : str) -> tuple:
    
    """
    Given a url, abbreviation, game_date scrape the corresponding html using requests.

    Returns html and response_code.
    """
    
    response_html = ''
    response_code = 0
    
    full_file_path = get_full_file_path(abbrev, date)
    
    time.sleep(2)  # sleep to not overwhelm bball-ref with requests (will get banned)

    
    with requests.Session() as session:
        response = session.get(url)  # request contents of url
        response_html = response.text   # parse contents for html
        response_code = response.status_code  # parse contents for status_code
        
        if response_code == 200:  # successful response
            
            with open(full_file_path, 'w') as html_file:  # write html to file
                html_file.write(response_html)
        
    return response_html, response_code


def check_for_html(url  : str 
              ,abbrev    : str
              ,game_date : datetime) -> tuple:

    """
    Given a url, abbreviation, game_date we look for the corresponding html locally.
    Write/read the html depending on whether or not it exists. 
    
    Returns the html and response_code of request for the html.
    """

    full_file_path = get_full_file_path(abbrev, game_date)

    if os.path.exists(full_file_path):
        logging.info(f'{abbrev} already exists locally. Reading...')
        response_code = 200 # simulate successful response

        with open(full_file_path, 'r') as read_file:
            html = read_file.read()
        
    else:
        logging.info(f'{abbrev} does not yet exist. Writing...')
        html, response_code = write_html(url, abbrev, game_date)

    return html, response_code


def get_all_games_on_date(game_date  : datetime 
                         ,home_teams : list):
    """
    For each date and list of home_teams, and search for the corresponding html
    for each game. (date / home_team combo) 

    If we have the html for the game already, we iterate to the next home_team.
    If we don't have the html, scrape it from bball ref and write it locally. 
    """
    
    format_date = game_date.strftime("%Y%m%d")
    
    for home_team in home_teams:
        game_url = f"https://www.basketball-reference.com/boxscores/pbp/{format_date}0{home_team}.html"
        abbrev = abbrev_url_to_file_name(game_url)
        game_html, game_response_code = check_for_html(game_url, abbrev, game_date)
        
    return 

def get_game_html_between_dates(start_game_date : datetime 
                                ,end_game_date  : datetime):
    """
    Given a start_date and end_date, get an inclusive list of all dates in between. 
    Iterates through date_list and looks for the corresponding html for each date.

    If we have the html for the date already, we iterate to the next home_team.
    If we don't have the html, scrape it from bball ref and write it locally. 
    """

    game_dates = get_date_range(start_game_date, end_game_date)    

    for game_date in game_dates:
        year, month, day = get_date_parts(game_date)
        date_url = f'https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}'
        date_file = f"{game_date.strftime('%Y-%m-%d')}.html"  # file_name is formatted yyyy-mm-dd.html
        date_html, date_response_code = check_for_html(date_url, date_file, game_date)
        
        home_teams = extract_home_teams(date_html, game_date)
        get_all_games_on_date(game_date, home_teams)
    
    return