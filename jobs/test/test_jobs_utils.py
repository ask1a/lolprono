from jobs import utils
import pandas as pd

def test_check_league():
    # Test case 1: League name contains a valid league
    assert utils.check_league('MSI 2024', ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']) == "keep"
    # Test case 2: League name contains an invalid league
    assert utils.check_league("LCK 2024", ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']) == "discard"
    # Test case 3: League name contains multiple valid leagues
    assert utils.check_league("MSI 2024 and LEC spring 2024", ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']) == "keep"
    # Test case 4: League name is empty
    assert utils.check_league("", ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']) == "discard"
    # Test case 5: Empty list of leagues
    assert utils.check_league("MSI 2024", []) == "discard"
    # Test case 6: League name contains a valid league with extra characters
    assert utils.check_league("MSI 2024 Playin", ['MSI 2024', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "keep"

# leagues = pd.DataFrame({'leaguename':['MSI 2024', 'LEC summer 2024']})
#
# df = pd.DataFrame({'league_name':['MSI 2024 Playin', 'LEC spring 2024 Playoff', 'LEC summer 2024']})
# df['keep'] = df['league_name'].apply(
#         lambda x: utils.check_league(x, leagues.leaguename.unique())
#     )
