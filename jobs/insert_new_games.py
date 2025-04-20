import utils 

if __name__ == '__main__':

    '''DEPRECATED
    scrap = utils.Scrap()
    df_raw = scrap.get_game_schedule_dataframe()
    df_clean =scrap.clean_schedule(df_raw)
    scrap.insert_future_games(df_clean)
    '''
    
    psr = utils.pandaScoreRequest()
    # Fetching game data
    for league in psr.leagues_panda:
        # Creating DF from panda score api call
        upcoming_df = psr.get_upcoming_games(league)
        # Inserting new plit if not already in the database
        psr.insert_new_league_serie(upcoming_df)
        # Cleaning df from existing games and inserting data in db
        df_clean = psr.clean_schedule(upcoming_df)
        psr.insert_future_games(df_clean)