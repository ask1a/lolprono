import utils

if __name__ == '__main__':
    scrap = utils.Scrap()
    df_raw = scrap.get_game_results_dataframe()
    df_clean =scrap.clean_results(df_raw)
    scrap.update_game_results(df_clean)