import utils

if __name__ == '__main__':

    '''DEPRECATED
    scrap = utils.Scrap()
    df_raw = scrap.get_game_results_dataframe()
    df_clean =scrap.clean_results(df_raw)
    scrap.update_game_results(df_clean)
    '''

    psr = utils.PandaScoreRequest()
    # Fetching game data
    for league in psr.leagues_panda:
        # Creating DF from panda score api call
        past_df = psr.get_past_games(league)
        # Cleaning df to update database
        df_clean = psr.clean_results(past_df)
        psr.update_game_results(df_clean)
