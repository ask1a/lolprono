import project.utils as u
import pandas as pd


def test_create_standing_table():
    df_input = pd.DataFrame([[1, 'askia', 1, 1, 3, 1, 3, 5], [1, 'askia', 2, 0, 3, 3, 1, 5],
                             [2, 'a', 1, 1, 3, 1, 3, 5],[2, 'a', 2, 3, 2, 3, 1, 5],
                             [2, 'a', 4, 1, 2, 1, 2, 3],[2, 'a', 5, 3, 2, 3, 1, 3],
                             [3, 'b', 1, 1, 3, 1, 3, 5],[3, 'b', 2, 3, 2, 3, 1, 5],
                             [4, 'c', 4, 1, 3, 1, 3, 5],[4, 'c', 5, 3, 2, 3, 1, 5]
                             ],
                            columns=['userid', 'username', 'gameid', 'prono_team_1', 'prono_team_2', 'score_team_1',
                                     'score_team_2', 'bo'])
    print(df_input)
    dico_result = u.create_standing_table(df_input)
    dico_expected = {}
    assert dico_expected == dico_result
