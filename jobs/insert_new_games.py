import utils 

if __name__ == '__main__':
    df = utils.get_game_schedule_dataframe()
    df_clean = utils.clean_schedule(df)
    utils.insert_future_games(df_clean)
    