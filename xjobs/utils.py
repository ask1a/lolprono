# Python core Librairies
import datetime
import re
import sqlite3

# Community Librairies
import pandas as pd
import requests

from bs4 import BeautifulSoup


def check_league(leagues: list[str], league_name: str) -> str:
    '''
    Check among leagues' items if one is contained in the league_name, used in a Lambda Function.
    This is comparing 2 strings between them. Not ideal, but it works.
    
    parameters:
    -----------
    leagues: list of strings
    league_name: String
    '''
    for league in leagues:
        if league in league_name and league_name!='': #invert condition?
            return 'keep'
    return 'discard'   

def assign_league_id(leagues_df: pd.DataFrame, league_name: str)->int:
    '''
    Assign the correct leagueid used in a Lambda Function.
    This is comparing 2 strings between them. Not ideal, but it works.
    
    parameters:
    -----------
    leagues_df: Pandas DataFrame containing leagueid and leaguename
    league_name: String
    '''
    for league in leagues_df['leaguename'].unique():
        if league in league_name: 
            return leagues_df[leagues_df['leaguename'] == league]['id'].values[0]
    return -1   

def clean_schedule(df: pd.DataFrame, db_path:str="instance/db.sqlite") -> pd.DataFrame:
    '''
    Function to clean Schedule DF before inserting it in DB
    
    parameters:
    -----------
    df: Pandas DataFrame containing games' informations.
    '''
    # Fetch leagues from instance database.
    con = sqlite3.connect(db_path)
    leagues = pd.read_sql_query("SELECT * FROM league", con)
    # If the league is in the list, we're keeping the games
    df['keep'] = df['league_name'].apply(
        lambda x: check_league(leagues.leaguename.unique(),x )
    )
    df['leagueid'] = df['league_name'].apply(
        lambda x: assign_league_id(leagues, x)
    )
    df = df[df['keep'] == 'keep']
    # Drop if team name is unknown
    df = df[df['team_1'] != 'unknown']
    df = df[df['team_2'] != 'unknown']
    # Fetch existing games 
    query = '''
        SELECT distinct
            game_datetime as db_datetime,
            team_1 as db_team_1, 
            team_2 as db_team_2
        FROM game
        WHERE
            date(game_datetime) >= current_date 
    '''
    future_games = pd.read_sql_query(query, con)
    # Formatting datetime as a string to permit merge:
    df['game_datetime'] = df['game_datetime'].apply(lambda x:
        x.strftime('%Y-%m-%d %H:%M:%S')
    )
    df= df.merge(future_games, how='left',
        left_on=['game_datetime', 'team_1', 'team_2'],
        right_on=['db_datetime', 'db_team_1', 'db_team_2']
    )
    # Keeping only games that are not yet inserted
    df = df[df['db_datetime'].isna()]
    # Only getting the number of games
    df['bo'] = df['bo'].apply(lambda x: int(x[-1]))
    # Reordering dataframe to match destination table.
    df = df[['leagueid','bo', 'game_datetime', 'team_1', 'team_2']]
    return df

def clean_results(df: pd.DataFrame, db_path:str="instance/db.sqlite") -> pd.DataFrame:
    '''
    Function to clean results DF before updating DB
    
    parameters:
    -----------
    df: Pandas DataFrame containing games' informations.
    '''
    # Formatting Score
    df['score_team_1'] = df['score'].apply(lambda x: x[0][0])
    df['score_team_2'] = df['score'].apply(lambda x: x[0][-1])
    # Fetch leagues from instance database.
    con = sqlite3.connect(db_path)
    leagues = pd.read_sql_query("SELECT * FROM league", con)
    # If the league is in the list, we're keeping the games
    df['keep'] = df['league_name'].apply(
        lambda x: check_league(leagues.leaguename.unique(), x)
    )
    df['leagueid'] = df['league_name'].apply(
        lambda x: assign_league_id(leagues, x)
    )
    # Formating Date:
    df['game_date'] = df['game_date'].apply(
        lambda x: datetime.datetime.strptime(x, '%A, %B %d, %Y').strftime('%Y-%m-%d')
    )
    # Only getting the number of games
    df['bo'] = df['bo'].apply(lambda x: int(x[-1]))
    # Reordering dataframe to match destination table.
    df = df[['leagueid','bo', 'game_date', 'team_1', 'team_2', 'score_team_1', 'score_team_2']]
    return df
    
def get_game_schedule_dataframe(html_content=None, testing=False) -> pd.DataFrame:
    
    '''
    Function to fetch future LOL games from the e-sportstats.com website and place it into a dataframe.
    
    parameters:
    -----------
    None
    '''
    # Fetching HTML
    if html_content:
        html_content_bs = BeautifulSoup(html_content)
    else:
        html = requests.get('https://e-sportstats.com/lol/matches')
        html_content_bs = BeautifulSoup(html.content)
    # Reaching div containning games schedule
    content = html_content_bs.body.main.find('div', class_='tournaments__list')
    # Inserting all elements in a list
    games = content.find_all('div')
    
    # Creating the shape a of finale DataFrame
    game_table = pd.DataFrame(
        columns=['league_name', 'game_date', 'game_time', 'bo', 'team_1', 'team_2', ]
    )
    
    for game in games:
        # Converting element to a string to ease regex usage: 
        # (Maybe not necessary)
        game = str(game)
        if testing:
            today = datetime.date(2024, 4, 27)
        else:
            today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        # If element is status, it gives us the date
        if '<div class="tournament__status">' in game:
            game_date = re.findall('(?<=span>\n)(.*?)(?=\n)', game.strip())[0]
            if 'Today' in game_date:
                game_date = today.strftime('%A, %B %d, %Y')
            elif 'Tomorrow' in game_date:
                game_date = tomorrow.strftime('%A, %B %d, %Y')
        # If element is stage, it gives us the league
        if '<div class="tournament__stage">' in game:
            league = re.findall('(?<=alt=")(.*?)(?=" )', game)[0]
        # If element is Item, it gives us the game.
        if '<div class="tournament__item">' in game: 
            if 'In Play' in game:
                continue
            # Removing string -today, because its concatenated to time, and makes the regex break.
            if '-today' in game:
                game = game.replace('-today', '')
                game_date = today.strftime('%A, %B %d, %Y')
            game = game.replace('-tomorrow', '')
            # Find game time
            game_time = re.findall('(?<=match__time">\n)(.*?)(?=\n)', game)[0]
            # Finding the BO type.
            bo = re.findall('(?<="match__type">)(.*?)(?=</span>)', game)[0]
            try:
                # If the regex breaks it means that the team names aren't available yet.  
                team_1 = re.findall('(?<=name-first" title=")(.*?)(?=">)', game)[0]
            except IndexError:
                team_1 = 'unknown'
            try:
                team_2 = re.findall('(?<=name-second" title=")(.*?)(?=">)', game)[0]
            except IndexError:
                team_2 = 'unknown'
            # Creating a 1 line dataframe with the infos of the game
            game_fetched = pd.DataFrame({
                'league_name': [league],
                # The fir status doesnt't give today's date so implementing it manually if it's the case.
                'game_date': [game_date], 
                'game_time': [game_time], 
                'bo': [bo],
                'team_1': [team_1],
                'team_2': [team_2]
            })
            # Adding it to the main dataframe.
            game_table = pd.concat([game_table, game_fetched])
    
    # Cleaning the Dataframe
    # Removing "Today" from the time string
    game_table['game_time'] = game_table['game_time'].apply(lambda x: x.replace(', Today', ''))
    game_table['game_time'] = game_table['game_time'].apply(lambda x: x.replace(', Tomorrow', ''))
    # Concatenating date and time to get the datetime.
    game_table['game_datetime'] = game_table['game_time'] + ' - ' + game_table['game_date']
    # Converting datetime string to datetime format
    game_table['game_datetime'] = game_table['game_datetime'].apply(
        lambda x: datetime.datetime.strptime(x, '%I:%M %p - %A, %B %d, %Y')
    )
    # Dropping unused columns
    game_table = game_table.drop(['game_date', 'game_time'], axis=1)
    # Reseting indexes
    game_table.reset_index(drop=True)        
    
    return game_table

def get_game_results_dataframe() -> pd.DataFrame:
    '''
    Function to fetch LOL games results from the e-sportstats.com website and place it into a dataframe.
    
    parameters:
    -----------
    None
    '''
    # Fetching HTML
    html = requests.get('https://e-sportstats.com/lol/matches-results')
    html_content = BeautifulSoup(html.content) 
    # Reaching div containnint games schedule
    content = html_content.body.main.find('div', class_='tournaments__list')
    # Inserting all elements in a list
    games = content.find_all('div')
    
    # Creating the shape a of finale DataFrame
    game_table = pd.DataFrame(
        columns=['league_name', 'game_date', 'game_time', 'bo', 'team_1', 'team_2', 'score']
    )
    
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    # Initializing game_date in case first div isn't 'tounament__status
    game_date = yesterday.strftime('%A, %B %d, %Y')
    for game in games:
        # Converting element to a string to ease regex usage: 
        # (Maybe not necessary)
        game = str(game)
        # If element is status, it gives us the date
        if '<div class="tournament__status">' in game:
            game_date = re.findall('(?<=span>\n)(.*?)(?=\n)', game.strip())[0]
            if 'Yesterday' in game_date:
                game_date = yesterday.strftime('%A, %B %d, %Y')
        # If element is stage, it gives us the league
        if '<div class="tournament__stage">' in game:
            league = re.findall('(?<=alt=")(.*?)(?=" )', game)[0]
        # If element is Item, it gives us the game.
        if '<div class="tournament__item">' in game: 
            game = game.replace(' match__name-lose', '')
            # Finding the BO type.
            bo = re.findall('(?<="match__type">)(.*?)(?=</span>)', game)[0]
            # If the regex breaks it means that the team names aren't available yet.  
            team_1 = re.findall('(?<=name-first" title=")(.*?)(?=">)', game)[0]
            team_2 = re.findall('(?<=name-second" title=")(.*?)(?=">)', game)[0]
            score = re.findall('(?<=score-value">\n)(.*?)((?=\n))', game)[0]
        # Creating a 1 line dataframe with the infos of the game
            game_fetched = pd.DataFrame({
                'league_name': [league],
                # The fir status doesnt't give today's date so implementing it manually if it's the case.
                'game_date': [game_date], 
                'bo': [bo],
                'team_1': [team_1],
                'team_2': [team_2], 
                'score': [score]
            })
            # Adding it to the main dataframe.
            game_table = pd.concat([game_table, game_fetched])
    
    # Reseting indexes
    game_table.reset_index(drop=True)        
    return game_table

def insert_future_games(df: pd.DataFrame) -> None:
    '''
    Insert the new games in the database
    
    parameters:
    -----------
    df: Pandas DataFrame containing cleaned and formated data.
    '''
    con_instance = sqlite3.connect("instance/db.sqlite")
    df.to_sql(name='game', con=con_instance, if_exists='append', index=False)
    
def update_game_results(df: pd.DataFrame) -> None:
    '''
    Update Games' results in the database
    
    parameters:
    -----------
    df: Pandas DataFrame containing cleaned and formated data.
    '''
    con_instance = sqlite3.connect("instance/db.sqlite")
    cursor = con_instance.cursor()
    df.to_sql(name='temp_results', con=con_instance, if_exists='replace', index=False)
    # Update game table using temp_results:
    for game in df.iterrows():
        league_id = game[1][0]
        bo = game[1][1]
        game_date = game[1][2]
        team_1 = game[1][3]
        team_2 = game[1][4]
        score_team_1 = game[1][5]
        score_team_2 = game[1][6]
        # Executing the update
        query = f"""
        UPDATE game
        SET score_team_1 = {score_team_1},
            score_team_2 = {score_team_2}
        WHERE
            leagueid = {league_id}
            AND bo = {bo}
            AND date(game_datetime) = date('{game_date}')
            AND team_1 = '{team_1}'
            AND team_2 = '{team_2}';
        """
        cursor.execute(query)
        con_instance.commit()
