import numpy as np
import pandas as pd


def eval_team_win(df: pd.DataFrame, val_team_1: str, val_team_2: str) -> np.array:
    return np.where((df[val_team_1] == df[val_team_2]) | (df[val_team_1].isna()) | (df[val_team_2].isna()), ''
                    , np.where(df[val_team_1] > df[val_team_2], 'team_1', 'team_2'),
                    )


def create_points_dataframe(pronos: pd.DataFrame):
    pronos['prono_team_win'] = eval_team_win(pronos, 'prono_team_1', 'prono_team_2')
    pronos['score_team_win'] = eval_team_win(pronos, 'score_team_1', 'score_team_2')
    pronos['prono_correct'] = np.where(pronos['prono_team_win'] == pronos['score_team_win'], 1, 0)
    pronos['score_exact'] = np.where(
        (pronos['prono_team_1'] == pronos['score_team_1']) & (pronos['prono_team_2'] == pronos['score_team_2']), 1, 0)

    game_odds = pronos[['gameid', 'prono_correct']].groupby(['gameid']).agg(['sum', 'count']).reset_index().values
    game_odds = pd.DataFrame(game_odds, columns=['gameid', 'nb_pronos_corrects', 'nb_pronos'])
    game_odds['odds'] = game_odds['nb_pronos'] / game_odds['nb_pronos_corrects']

    pronos = pronos.merge(game_odds, on='gameid')
    pronos['points'] = np.where(pronos['score_exact'] == 1, pronos['odds'] * (pronos['bo'] // 2 + 1), pronos['odds'])
    pronos['points'] = np.where(pronos['prono_correct'] == 1, round(pronos['points'],2), 0)

    return pronos


def create_standing_table(pronos: pd.DataFrame) -> list:
    pronos = create_points_dataframe(pronos)
    pronos = pronos.dropna()
    recap_score = pronos[['userid', 'username', 'prono_correct', 'score_exact', 'points']].groupby(
        ['userid', 'username']).sum()
    recap_score = recap_score.sort_values('points', ascending=False)
    recap_score = recap_score.reset_index(level=['userid', 'username'])
    recap_score['points'] = recap_score['points'].round(2)
    recap_score = recap_score.drop(columns=['userid']).to_dict("records")
    return recap_score
