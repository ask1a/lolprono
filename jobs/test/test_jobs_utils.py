from jobs import utils

def test_check_league():
    # Test case 1: League name contains a valid league
    assert utils.check_league('MSI 2024', ['MSI 2024 Playin', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "keep"
    # Test case 2: League name contains an invalid league
    assert utils.check_league("MSI 2024", ['LCK 2024 Playin', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "discard"
    # Test case 3: League name contains multiple valid leagues
    assert utils.check_league("MSI 2024 and LCK 2024", ['MSI 2024 Playin', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "discard"
    # Test case 4: League name is empty
    #assert utils.check_league("", ['MSI 2024 Playin', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "discard"
    # Test case 5: Empty list of leagues
    assert utils.check_league("MSI 2024", []) == "discard"
    # Test case 6: League name contains a valid league with extra characters
    assert utils.check_league("MSI 2024 Playin", ['MSI 2024', 'LEC spring 2024 Playoff', 'LEC summer 2024']) == "discard"
