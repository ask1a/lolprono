import numpy as np
import pandas as pd

def create_points_dataframe(pronos: pd.DataFrame):
    pronos['prono_team_win'] = np.where(
        (pronos['prono_team_1'] > pronos['prono_team_2']) & (pronos['prono_team_1'] != pronos['prono_team_2']),
        'team_1',
        'team_2')
    pronos['score_team_win'] = np.where(
        (pronos['score_team_1'] > pronos['score_team_2']) & (pronos['score_team_1'] != pronos['score_team_2']),
        'team_1',
        'team_2')
    pronos['prono_correct'] = np.where(pronos['prono_team_win'] == pronos['score_team_win'], 1, 0)
    pronos['score_exact'] = np.where(
        (pronos['prono_team_1'] == pronos['score_team_1']) & (pronos['prono_team_2'] == pronos['score_team_2']), 1, 0)

    game_odds = pronos[['gameid', 'prono_correct']].groupby(['gameid']).agg(['sum', 'count']).reset_index().values
    game_odds = pd.DataFrame(game_odds, columns=['gameid', 'nb_pronos_corrects', 'nb_pronos'])
    game_odds['odds'] = game_odds['nb_pronos'] / game_odds['nb_pronos_corrects']

    pronos = pronos.merge(game_odds, on='gameid')
    pronos['points'] = np.where(pronos['score_exact'] == 1, pronos['odds'] * (pronos['bo'] // 2 + 1), pronos['odds'])
    pronos['points'] = np.where(pronos['prono_correct'] == 1, pronos['points'], 0)
    return pronos
def create_standing_table(pronos: pd.DataFrame) -> list:
    # pronos['prono_team_win'] = np.where(
    #     (pronos['prono_team_1'] > pronos['prono_team_2']) & (pronos['prono_team_1'] != pronos['prono_team_2']),
    #     'team_1',
    #     'team_2')
    # pronos['score_team_win'] = np.where(
    #     (pronos['score_team_1'] > pronos['score_team_2']) & (pronos['score_team_1'] != pronos['score_team_2']),
    #     'team_1',
    #     'team_2')
    # pronos['prono_correct'] = np.where(pronos['prono_team_win'] == pronos['score_team_win'], 1, 0)
    # pronos['score_exact'] = np.where(
    #     (pronos['prono_team_1'] == pronos['score_team_1']) & (pronos['prono_team_2'] == pronos['score_team_2']), 1, 0)
    #
    # game_odds = pronos[['gameid', 'prono_correct']].groupby(['gameid']).agg(['sum', 'count']).reset_index().values
    # game_odds = pd.DataFrame(game_odds, columns=['gameid', 'nb_pronos_corrects', 'nb_pronos'])
    # game_odds['odds'] = game_odds['nb_pronos'] / game_odds['nb_pronos_corrects']
    #
    # pronos = pronos.merge(game_odds, on='gameid')
    # pronos['points'] = np.where(pronos['score_exact']==1,pronos['odds'] * (pronos['bo'] // 2 + 1),pronos['odds'])
    # pronos['points'] = np.where(pronos['prono_correct']==1,pronos['points'],0)
    pronos = create_points_dataframe(pronos)

    recap_score = pronos[['userid', 'username', 'prono_correct', 'score_exact', 'points']].groupby(
        ['userid', 'username']).sum()
    recap_score = recap_score.sort_values('points', ascending=False)
    recap_score = recap_score.reset_index(level=['userid', 'username'])
    recap_score = recap_score.drop(columns=['userid']).to_dict("records")
    return recap_score


