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

def abbrev_url_to_file_name(url : str) -> str:
    """
    Abbreviate the given url to be suitable for a file name. (remove commonalities/illegal characters)

    Return cleaned abbrevation of url.
    """

    # define illegal characters and their replacements
    replace_dict = {'?'  : ''
                    ,'&' : ''
                    ,'=' : ''
                    ,'/' : '_'}

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
    file_path = os.path.abspath(os.path.real_path(full_file_path))  # ensure file path is readable (changes /extract/../data to /lawlers/data/)

    # ensure file path exists
    if not os.path.exists(file_path):
        os.makedirs(file_path)  # if not exists, create it
        logging.info(f"New directory created: {file_path}")

    full_file_path = file_path + file_name  # add file_name to get full_file_path

    return full_file_path


def write_html_from_url(url   : str
                        ,date : datetime):
    """
    Given url, retrieve html from url. Then write the html to file with abbreviated name in the given date directory.

    Return response code of url response.
    """

    resp_code = 0  # initialize in case we do not get a resp_code from response
    file_name = abbrev_url_to_file_name(url)  # abbreviate url to file_name
    full_file_path = get_full_file_path(file_name, date)  # get full path of file

    with requests.Session() as session:
        time.sleep(2)  # add delay to not overrun bball-ref with requests
        
        try:
            response = session.get(url)  # request contents of url
            resp_code = response.status_code  
            resp_html = response.text  # this is the html of the url    

            if resp_code == 200:  # status 200 means request was successful
                with open(full_file_path, 'w') as target_file:
                    target_file.write(resp_html)  # write the html to the corresponding file

        except Exception as e:
            logging.info(f"The following error occurred when accessing/writing the html from {url} :")
            logging.info(f"{e}")

    return resp_html, resp_code


def get_game_date_html(date : datetime) -> list:
    """
    Given a date, check if we have html for that date. If not, attempt to retrieve/write html.
    
    If we get html for the date, get the home teams on date.

    Returns list of home teams. 
    """
    
    home_teams = []

    year, month, day = get_date_parts(date)  # split date parts for url formatting
    format_date = date.strftime("%Y%m%d")  # used for identifying hometeams in extract_home_teams()
    date_url = f"https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"

    file_name = abbrev_url_to_file_name(date_url)  # abbreviate url to file_name
    full_file_path = get_full_file_path(file_name, date)  # get full path of file

    # if we have the html locally, read it
    if os.path.isfile(full_file_path):
        logging.info(f"{file_name} exists locally. Attempting to read...")
        resp_code = 200 # simulate successful response
        with open(full_file_path, 'r') as target_file:
            resp_html = f.read()
    
    # if we don't have html locally, retrieve/write it and get home_teams.
    else:
        resp_html, resp_code = write_html_from_url(date_url, date)  # attempt to write html
        if resp_code == 200:
            home_teams = extract_home_teams(resp_html, format_date)
        else:
            logging.error(f"Error occurred when accessing {date_url}")
    
    return home_teams, resp_code


def extract_home_teams(date_html : str
                    ,format_date : str) -> list:
    """
    Gets soup from html and parses soup to get list of home_teams.
    
    Returns list of home team.
    """
    
    date_soup = get_soup(date_html)  # turn html to readable soup

    a_elements = date_soup.find_all('a')
    box_scores = [bs for bs in a_elements if f'/boxscores/{format_date}' in str(bs)]  # get all box_score elements
    home_teams = [str(bs).split('.html')[0][-3:] for bs in box_scores]  # each home team appears in 3 letter abbrev before ".html"
    clean_home_teams = set([team for team in home_teams if team in team_dict.keys()]) # verify teams are in dict, get unique set of teams
    
    return list(clean_home_teams)


def write_game_html(game_date : datetime
                 ,home_team : str) -> dict:
    """
    Given home_team and date, look for the game html locally. If exists,
    """
    
    format_date = game_date.strftime("%Y%m%d")  # url reads date without dashes
    
    pbp_url = f"https://www.basketball-reference.com/boxscores/pbp/{format_date}0{home_team}.html"  # play-by-play (pbp) will have scores
    file_name = abbrev_url_to_file_name(pbp_url)
    full_file_path = get_full_file_path(file_name, game_date)

    # if we have the html locally, read it
    if os.path.isfile(full_file_path):
        logging.info(f"{file_name} exists locally. Moving to next game.")
        resp_code = 200  # simulate successful response
    
    # if we don't have html locally, retrieve/write it and get home_teams.
    else:
        resp_html, resp_code = write_html_from_url(pbp_url, date)  # attempt to write html

    
    return resp_html, resp_code

def get_date_range(start_game_date : str
                  ,end_game_date   : str) -> tuple:
    """
    Takes start date and end date and does 2 things:
        1. Ensure dates are formatted properly
        2. Generates a list of dates in between start and end (inclusive)
    
    Returns formatted dates and date_list
    """

    try:
        start_game_date = datetime.strptime(start_game_date, '%Y-%m-%d')  # ensure dates are formatted properly
        end_game_date = datetime.strptime(end_game_date, '%Y-%m-%d')
        day_delta = (end_game_date - start_game_date).days  # get number of days between both dates
        game_dates = [start_game_date + timedelta(days=i) for i in range(0, day_delta + 1)]  # get list of dates in between start and end dates
    
    except Exception as e:
        print('There is something wrong with the dates inputted. Ensure your dates formatted as YYYY-MM-DD.')
        logging.error(f"The following error occurred when trying to generate a date range:\n{e}")

    return start_game_date, end_game_date, game_dates 


def get_game_html_between_dates(start_game_date : str
                               ,end_game_date   : str) -> dict:
    """
    Given 2 dates, get list of all dates in between them (inclusive). 
    Then find all games on those dates. For each game, check if the game data (html) is stored locally. If not, retrieve the html and store locally
    
    Returns dictionary of game_dicts.
    """

    logging.info(f"Searching for game data in following date range: {start_game_date} - {end_game_date}\n")
    start_game_date, end_game_date, game_dates = get_date_range(start_game_date, end_game_date)  # get list of dates in between start and end (inclusive)
    
    # For each game_date, attempt to find games. 
    # If a game is found, check to see if the html for the game is stored locally yet.
    ## If html is stored locally, move to next game/date.
    ## If html is not stored locally, attempt to retrieve from internet and write the html locally.
    # If no games are found, move to next date.

    for game_date in game_dates:
        game_date_str = game_date.strftime("%Y-%m-%d")

        home_teams, resp_code = get_game_date_html(game_date)  # read or extract game_date_html and get home_teams on_date

        if resp_code == 200:  
            logging.info(f"Home teams found on {game_date_str}: {home_teams}")
            write_game_html(game_date, home_teams)
        
        else:
            logging.info(f"Issue occurred while getting games on: {game_date_str}")
            break

    return 