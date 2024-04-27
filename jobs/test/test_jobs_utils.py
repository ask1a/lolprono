from jobs import utils
import pandas as pd

def test_check_league():
    # Test case 1: League name contains a valid league
    assert utils.check_league(['MSI 2024', 'LEC spring 2024', 'LEC summer 2024'], 'MSI 2024') == "keep"
    # Test case 2: League name contains an invalid league
    assert utils.check_league(['MSI 2024', 'LEC spring 2024', 'LEC summer 2024'], "LCK 2024") == "discard"
    # Test case 3: League name contains multiple valid leagues
    assert utils.check_league(['MSI 2024', 'LEC spring 2024', 'LEC summer 2024'], "MSI 2024 and LEC spring 2024") == "keep"
    # Test case 4: League name is empty
    assert utils.check_league(['MSI 2024', 'LEC spring 2024', 'LEC summer 2024'], "") == "discard"
    # Test case 5: Empty list of leagues
    assert utils.check_league([], "MSI 2024",) == "discard"
    # Test case 6: League name contains a valid league with extra characters
    assert utils.check_league(['MSI 2024', 'LEC spring 2024 Playoff', 'LEC summer 2024'], "MSI 2024 Playin") == "keep"


def test_assign_league_id():
    # example DataFrame for tests
    data = {'id': [3, 1, 2], 'leaguename': ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']}
    leagues_df = pd.DataFrame(data)

    # Test case 1 : corresponding
    assert utils.assign_league_id(leagues_df, 'LEC spring 2024') == 1
    # Test case 2 : partial
    assert utils.assign_league_id(leagues_df, 'MSI 2024 playin') == 3
    # Test case 2bis : barely correspond
    assert utils.assign_league_id(leagues_df, 'MSI 202') == -1
    # Test case 3 : no match
    assert utils.assign_league_id(leagues_df, 'LCK 2024') == -1
    # Test case 4 : empty
    assert utils.assign_league_id(leagues_df, '') == -1
    # Test case 5 : doesnt exist
    assert utils.assign_league_id(leagues_df, 'MLS') == -1
