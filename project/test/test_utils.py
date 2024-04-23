import project.utils as u
import pandas as pd
import numpy as np


def test_eval_team_win():
    # Créez un DataFrame de test
    data = {
        'score_team_1': [1, 2, 3],
        'score_team_2': [2, 2, 2]
    }
    df = pd.DataFrame(data)

    # Testez l'évaluation des équipes gagnantes
    result = u.eval_team_win(df, 'score_team_1', 'score_team_2')
    expected_result = np.array(['team_2', '', 'team_1'])
    np.testing.assert_array_equal(result, expected_result)


def test_create_standing_table():
    df_input = pd.DataFrame([[1, 'askia', 1, 1, 3, 1, 3, 5], [1, 'askia', 2, 0, 1, 0, 1, 1],
                             [2, 'a', 1, 1, 3, 1, 3, 5], [2, 'a', 2, 0, 1, 0, 1, 1],
                             [2, 'a', 4, 1, 2, 1, 2, 3], [2, 'a', 5, 1, 2, 2, 1, 3],
                             [3, 'b', 1, 2, 3, 1, 3, 5], [3, 'b', 2, 1, 0, 0, 1, 1],
                             [4, 'c', 4, 2, 0, 1, 2, 3], [4, 'c', 2, 1, 0, 0, 1, 1],
                             [5, 'd', 5, 2, 0, 2, 1, 3], [6, 'e', 5, 2, 1, 2, 1, 3]
                             ],
                            columns=['userid', 'username', 'gameid', 'prono_team_1', 'prono_team_2', 'score_team_1',
                                     'score_team_2', 'bo'])
    list_result = u.create_standing_table(df_input)
    list_expected = [{'username': 'a', 'prono_correct': 3, 'score_exact': 3, 'points': 9.0},
                     {'username': 'askia', 'prono_correct': 2, 'score_exact': 2, 'points': 5.0},
                     {'username': 'e', 'prono_correct': 1, 'score_exact': 1, 'points': 3.0},
                     {'username': 'd', 'prono_correct': 1, 'score_exact': 0, 'points': 1.5},
                     {'username': 'b', 'prono_correct': 1, 'score_exact': 0, 'points': 1.0},
                     {'username': 'c', 'prono_correct': 0, 'score_exact': 0, 'points': 0.0}]
    assert list_expected == list_result
