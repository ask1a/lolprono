import utils 

if __name__ == '__main__':
    scrap = utils.Scrap()
    df_raw = scrap.get_game_schedule_dataframe()
    df_clean =scrap.clean_schedule(df_raw)
    scrap.insert_future_games(df_clean)