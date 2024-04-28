from jobs import utils
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas import Timestamp
import pytest
from pathlib import Path


def test_check_league():
    # Declaring call
    test_scrap = utils.Scrap(test_job=True)
    # Test case 1: League name contains a valid league
    test_scrap.leagues = pd.DataFrame({'leaguename': ['Mid-Season Invitational 2024']})
    assert test_scrap.check_league('Mid-Season Invitational 2024') == "keep"
    # Test case 2: League name contains an invalid league
    assert test_scrap.check_league( "LCK 2024") == "discard"
    # Test case 3: League name contains multiple valid leagues
    test_scrap.leagues = pd.DataFrame({'leaguename': ['LEC spring 2024']})
    assert test_scrap.check_league("MSI 2024 and LEC spring 2024") == "keep"
    # Test case 4: League name is empty
    assert test_scrap.check_league("") == "discard"
    # Test case 5: League name contains a valid league with extra characters
    test_scrap.leagues = pd.DataFrame({'leaguename': ['Mid-Season Invitational 2024']})
    assert test_scrap.check_league( "Mid-Season Invitational 2024 Playin") == "keep"
    # Test case 6: Empty list of leagues
    test_scrap.leagues = pd.DataFrame({'leaguename': []})
    assert test_scrap.check_league("MSI 2024") == "discard"


def test_assign_league_id():
    # example DataFrame for tests
    data = {'id': [3, 1, 2], 'leaguename': ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']}
    # Declaring class
    test_scrap = utils.Scrap(test_job=True)
    test_scrap.leagues = pd.DataFrame(data)
    # Test case 1 : corresponding
    assert test_scrap.assign_league_id('LEC spring 2024') == 1
    # Test case 2 : partial
    assert test_scrap.assign_league_id('MSI 2024 playin') == 3
    # Test case 2bis : barely correspond
    assert test_scrap.assign_league_id('MSI 202') == -1
    # Test case 3 : no match
    assert test_scrap.assign_league_id('LCK 2024') == -1
    # Test case 4 : empty
    assert test_scrap.assign_league_id('') == -1
    # Test case 5 : doesnt exist
    assert test_scrap.assign_league_id('MLS') == -1


def test_get_game_schedule_dataframe(html_content, expected_df_for_get_game_schedule_dataframe):
    rslt_df = utils.get_game_schedule_dataframe(html_content, testing=True)
    expected_df = expected_df_for_get_game_schedule_dataframe

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_clean_schedule(expected_df_for_get_game_schedule_dataframe,expected_df_for_clean_schedule):
    home = Path(__file__).resolve().parent.parent.parent
    db_path = home / 'instance/db.sqlite'
    rslt_df = utils.clean_schedule(expected_df_for_get_game_schedule_dataframe,db_path,True)
    expected_df = expected_df_for_clean_schedule

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


@pytest.fixture
def html_content():
    home = Path(__file__).resolve().parent.parent.parent
    file_path = home / 'jobs/test/esportstats_matchs.bin'
    with open(file_path, "rb") as f:
        html_content_byte = f.read()
    return html_content_byte


@pytest.fixture
def expected_df_for_clean_schedule():
    return pd.DataFrame(
        {
            'leagueid': [3, 3, 3, 3], 'bo': [3, 3, 3, 3],
            'game_datetime': ['2024-05-01 08:00:00', '2024-05-01 11:00:00', '2024-05-02 08:00:00',
            '2024-05-02 11:00:00'], 'team_1': ['FLY', 'T1', 'FNC', 'TES'],
            'team_2': ['PSG', 'EST', 'GAM', 'LLL']
        }
    )


@pytest.fixture
def expected_df_for_get_game_schedule_dataframe():
    return pd.DataFrame(
        {'league_name':
            [
                'LDL Split 2 2024 Group B', 'LCO Split 1 2024 Playoffs',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'EMEA Masters Spring 2024 Playoffs',
                'CBLOL Academy Split 1 2024 Playoffs', 'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group B', 'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'LDL Split 2 2024 Group B', 'LDL Split 2 2024 Group B',
                'Mid-Season Invitational 2024 Play-In: Group B',
                'Mid-Season Invitational 2024 Play-In: Group B',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'LDL Split 2 2024 Group B', 'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A',
                'Mid-Season Invitational 2024 Play-In: Group B',
                'Mid-Season Invitational 2024 Play-In: Group B',
                'LDL Split 2 2024 Group B', 'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'LDL Split 2 2024 Group B',
                'Mid-Season Invitational 2024 Play-In: Group B',
                'LDL Split 2 2024 Group B', 'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A', 'LDL Split 2 2024 Group A',
                'Mid-Season Invitational 2024 Playoffs',
                'Ignis Cup Split 1 2024 Playoffs', 'Ignis Cup Split 1 2024 Playoffs'],
                'bo': ['BO3', 'BO5', 'BO3', 'BO3', 'BO5', 'BO5', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3',
                        'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3',
                        'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3',
                        'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO3', 'BO5',
                        'BO3', 'BO3'],
                'team_1': ['TESC', 'GZ', 'BLGJ', 'RYL', 'ES', 'VKS.A', 'WEA', 'IGY', 'FPB', 'TT.Y',
                        'WEA', 'MAX', 'OMG.A', 'LGDY', 'FLY', 'T1', 'RAP', 'MJ', 'FNC', 'TES',
                        'BLGJ', 'EDGY', 'RYL', 'unknown', 'unknown', 'RAP', 'WBG.Y', 'JDM',
                        'unknown', 'unknown', 'MJ', 'UPA', 'TT.Y', 'EDGY', 'unknown', 'JJH',
                        'unknown', 'WBG.Y', 'MJ', 'IGY', 'EDGY', 'RYL', 'LNGA', 'unknown', 'PNG',
                        'LMEC'],
                'team_2': ['AL.Y', 'ANC', 'OMG.A', 'TT.Y', 'BJK', 'PNG.A', 'JJH', 'EDGY', 'LNGA', 'JDM',
                        'UPA', 'AL.Y', 'IGY', 'FPB', 'PSG', 'EST', 'WBG.Y', 'TESC', 'GAM', 'LLL',
                        'TT.Y', 'LNGA', 'OMG.A', 'unknown', 'unknown', 'JJH', 'WEA', 'FPB',
                        'unknown', 'unknown', 'MAX', 'AL.Y', 'LGDY', 'RYL', 'unknown', 'TESC',
                        'unknown', 'UPA', 'RAP', 'BLGJ', 'TT.Y', 'JDM', 'LGDY', 'unknown', 'IME',
                        'CVN'],
                'game_datetime': [Timestamp('2024-04-28 06:00:00'), Timestamp('2024-04-28 07:00:00'),
                    Timestamp('2024-04-28 08:00:00'), Timestamp('2024-04-28 10:00:00'),
                    Timestamp('2024-04-28 15:00:00'), Timestamp('2024-04-28 16:00:00'),
                    Timestamp('2024-04-29 06:00:00'), Timestamp('2024-04-29 08:00:00'),
                    Timestamp('2024-04-29 10:00:00'), Timestamp('2024-04-30 06:00:00'),
                    Timestamp('2024-04-30 08:00:00'), Timestamp('2024-04-30 10:00:00'),
                    Timestamp('2024-05-01 06:00:00'), Timestamp('2024-05-01 08:00:00'),
                    Timestamp('2024-05-01 08:00:00'), Timestamp('2024-05-01 11:00:00'),
                    Timestamp('2024-05-01 10:00:00'), Timestamp('2024-05-02 06:00:00'),
                    Timestamp('2024-05-02 08:00:00'), Timestamp('2024-05-02 11:00:00'),
                    Timestamp('2024-05-02 08:00:00'), Timestamp('2024-05-02 10:00:00'),
                    Timestamp('2024-05-03 06:00:00'), Timestamp('2024-05-03 08:00:00'),
                    Timestamp('2024-05-03 11:00:00'), Timestamp('2024-05-03 08:00:00'),
                    Timestamp('2024-05-03 10:00:00'), Timestamp('2024-05-04 06:00:00'),
                    Timestamp('2024-05-04 08:00:00'), Timestamp('2024-05-04 11:00:00'),
                    Timestamp('2024-05-04 08:00:00'), Timestamp('2024-05-04 10:00:00'),
                    Timestamp('2024-05-05 06:00:00'), Timestamp('2024-05-05 10:00:00'),
                    Timestamp('2024-05-05 08:00:00'), Timestamp('2024-05-05 08:00:00'),
                    Timestamp('2024-05-05 11:00:00'), Timestamp('2024-05-06 06:00:00'),
                    Timestamp('2024-05-06 10:00:00'), Timestamp('2024-05-06 08:00:00'),
                    Timestamp('2024-05-07 06:00:00'), Timestamp('2024-05-07 08:00:00'),
                    Timestamp('2024-05-07 10:00:00'), Timestamp('2024-05-07 09:00:00'),
                    Timestamp('2024-05-07 16:00:00'), Timestamp('2024-05-07 19:00:00')]
            }
        )