import utils

if __name__ == '__main__':
    df = utils.get_game_results_dataframe()
    df_clean = utils.clean_results(df)
    utils.update_game_results(df_clean)