from jobs import utils
import pandas as pd
from pandas.testing import assert_frame_equal
from pandas import Timestamp
import pytest
from pathlib import Path

''' DEPRECATED 
def test_check_league():
    # Declaring class
    test_panda = utils.Scrap(test_job=True)
    # Test case 1: League name contains a valid league
    test_panda.leagues = pd.DataFrame({'leaguename': ['LEC Spring 2025']})
    assert test_panda.check_league('LEC Spring 2025') == "keep"
    # Test case 2: League name contains an invalid league
    assert test_panda.check_league("LCK 2024") == "discard"
    # Test case 3: League name contains multiple valid leagues DISCARDED
    test_panda.leagues = pd.DataFrame({'leaguename': ['LEC spring 2024']})
    assert test_panda.check_league("MSI 2024 and LEC spring 2024") == "keep"
    # Test case 4: League name is empty
    assert test_panda.check_league("") == "discard"
    # Test case 5: League name contains a valid league with extra characters
    test_panda.leagues = pd.DataFrame({'leaguename': ['Mid-Season Invitational 2024']})
    assert test_panda.check_league( "Mid-Season Invitational 2024 Playin") == "keep"
    # Test case 6: Empty list of leagues
    test_panda.leagues = pd.DataFrame({'leaguename': []})
    assert test_panda.check_league("MSI 2024") == "discard"
'''

def test_assign_league_id():
    # example DataFrame for tests
    data = {'id': [3, 1, 2], 'leaguename': ['MSI 2024', 'LEC spring 2024', 'LEC summer 2024']}
    # Declaring class
    test_panda = utils.Scrap(test_job=True)
    test_panda.leagues = pd.DataFrame(data)
    # Test case 1 : corresponding
    assert test_panda.assign_league_id('LEC spring 2024') == 1
    # Test case 2 : partial
    assert test_panda.assign_league_id('MSI 2024 playin') == 3
    # Test case 2bis : barely correspond
    assert test_panda.assign_league_id('MSI 202') == -1
    # Test case 3 : no match
    assert test_panda.assign_league_id('LCK 2024') == -1
    # Test case 4 : empty
    assert test_panda.assign_league_id('') == -1
    # Test case 5 : doesnt exist
    assert test_panda.assign_league_id('MLS') == -1


def test_identifty_team_names(expected_df_for_clean_schedule):
    test_panda = utils.Scrap(test_job=True)
    test_df = pd.DataFrame(
        {
            'leagueid': [3, 3, 3, 3], 'bo': [3, 3, 3, 3],
            'game_datetime': ['2024-05-01 08:00:00', '2024-05-01 11:00:00', '2024-05-02 08:00:00',
            '2024-05-02 11:00:00'], 'team_1': ['FLY', 'T1', 'FNC', 'TES'],
            'team_2': ['PSG', 'EST', 'GAM', 'LLL']
        }
    )
    test_df = test_panda.identifty_team_names(test_df)
    assert_frame_equal(test_df.reset_index(drop=True), expected_df_for_clean_schedule.reset_index(drop=True), check_dtype=False)


def test_get_game_schedule_dataframe(html_content_schedule, expected_df_for_get_game_schedule_dataframe):
    test_panda = utils.Scrap(test_job=True)
    rslt_df = test_panda.get_game_schedule_dataframe(html_content_schedule)
    expected_df = expected_df_for_get_game_schedule_dataframe

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_clean_schedule(expected_df_for_get_game_schedule_dataframe,expected_df_for_clean_schedule):
    test_panda = utils.Scrap(test_job=True)
    rslt_df = test_panda.clean_schedule(expected_df_for_get_game_schedule_dataframe)
    expected_df = expected_df_for_clean_schedule

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_clean_results(expected_df_for_get_game_results_dataframe, expected_df_for_clean_results):
    test_panda = utils.Scrap(test_job=True)
    rslt_df = test_panda.clean_results(expected_df_for_get_game_results_dataframe)
    print(rslt_df)
    expected_df = expected_df_for_clean_results
    print(expected_df)

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_get_game_results_dataframe(html_content_results, expected_df_for_get_game_results_dataframe):
    test_panda = utils.Scrap(test_job=True)
    results_df = test_panda.get_game_results_dataframe(html_content_results)
    results_expected_df = expected_df_for_get_game_results_dataframe
    assert_frame_equal(results_df.reset_index(drop=True), results_expected_df.reset_index(drop=True), check_dtype=False)


@pytest.fixture
def html_content_schedule():
    home = Path(__file__).resolve().parent.parent.parent
    file_path = home / 'jobs/test/esportstats_matchs.bin'
    with open(file_path, "rb") as f:
        html_content_byte = f.read()
    return html_content_byte

@pytest.fixture
def html_content_results():
    home = Path(__file__).resolve().parent.parent.parent
    file_path = home / 'jobs/test/lol_esport_matches.txt'
    with open(file_path, "r", encoding='utf-8') as f:
        html_content_byte = f.read()
    return html_content_byte

@pytest.fixture
def expected_df_for_clean_schedule():
    return pd.DataFrame(
        {
            'leagueid': [3, 3, 3, 3], 'bo': [3, 3, 3, 3],
            'game_datetime': ['2024-05-01 08:00:00', '2024-05-01 11:00:00', '2024-05-02 08:00:00',
            '2024-05-02 11:00:00'], 'team_1': ['Flyquest', 'T1', 'Fnatic', 'Top Esport'],
            'team_2': ['PSG Talon', 'Estral Esport', 'GAM Esport', 'Loud']

        }
    )


@pytest.fixture
def expected_df_for_clean_results():
    return pd.DataFrame(
        {
            'leagueid': [3, 3], 'bo': [3, 3],
            'game_date': ['2024-04-26', '2024-04-26'], 'team_1': ['T1', 'Flyquest'],
            'team_2': ['Estral Esport', 'PSG Talon'],
            'score_team_1': ['2', '2'],
            'score_team_2': ['0', '1']
        }
    )


@pytest.fixture
def expected_df_for_get_game_schedule_dataframe():
    return pd.DataFrame(
        {
            'league_name': [
                    'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 
                    'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 
                    'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 
                    'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025',
                    'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 
                    'LEC Spring 2025', 'LEC Spring 2025'
                ],
            'bo': [
                    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
                ],
            'team_1': [
                    'TH', 'G2', 'SK', 'MKOI', 'G2', 'MKOI', 'G2', 'MKOI', 'TH', "VIT", 
                    'FNC', 'KC', 'GX', 'G2', 'TH', 'MKOI', 'G2', 'KC', 'VIT', 'KC', 'TH', 'MKOIs'
                ],
            'team_2': [
                    'VIT', 'BDS', 'RGE', 'VIT', 'GX', 'FNC', 'FNC', 'GX', 'SK', 'BDS', 'BDS', 'RGE',
                    'BDS', 'VIT', 'FNC', 'SK', 'SK', 'VIT', 'SK', 'G2', 'GX', 'RGE'
                ],
            'game_datetime': [
                    Timestamp('2025-04-20 15:00:00'), Timestamp('2025-04-20 17:00:00'),
                    Timestamp('2025-04-21 15:00:00'), Timestamp('2025-04-21 17:00:00'),
                    Timestamp('2025-04-26 13:00:00'), Timestamp('2025-04-26 15:00:00'),
                    Timestamp('2025-04-27 13:00:00'), Timestamp('2025-04-27 15:00:00'),
                    Timestamp('2025-04-28 15:00:00'), Timestamp('2025-04-28 17:00:00'),
                    Timestamp('2025-05-03 15:00:00'), Timestamp('2025-05-03 17:00:00'),
                    Timestamp('2025-05-04 15:00:00'), Timestamp('2025-05-04 17:00:00'),
                    Timestamp('2025-05-05 15:00:00'), Timestamp('2025-05-05 17:00:00'),
                    Timestamp('2025-05-10 15:00:00'), Timestamp('2025-05-10 17:00:00'),
                    Timestamp('2025-05-11 15:00:00'), Timestamp('2025-05-11 17:00:00'),
                    Timestamp('2025-05-12 15:00:00'), Timestamp('2025-05-12 17:00:00')
                ]
            }
        )

@pytest.fixture
def expected_df_for_get_game_results_dataframe():
    return pd.DataFrame(
        {'league_name':
            [
                'Mid-Season Invitational 2024 Play-In: Group A',
                'Mid-Season Invitational 2024 Play-In: Group A',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'CBLOL Academy Split 1 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'LCO Split 1 2024 Playoffs',
                'CBLOL Academy Split 1 2024 Playoffs',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A',
                'CBLOL Academy Split 1 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'CBLOL Academy Split 1 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group A',
                'LDL Split 2 2024 Group B',
                'LDL Split 2 2024 Group B',
                'EMEA Masters Spring 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs',
                'EMEA Masters Spring 2024 Playoffs'
            ],
            'game_date': [
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Monday, April 29, 2024',
                'Monday, April 29, 2024',
                'Monday, April 29, 2024',
                'Sunday, April 28, 2024',
                'Sunday, April 28, 2024',
                'Sunday, April 28, 2024',
                'Sunday, April 28, 2024',
                'Sunday, April 28, 2024',
                'Sunday, April 28, 2024',
                'Saturday, April 27, 2024',
                'Saturday, April 27, 2024',
                'Saturday, April 27, 2024',
                'Saturday, April 27, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Friday, April 26, 2024',
                'Thursday, April 25, 2024',
                'Thursday, April 25, 2024',
                'Thursday, April 25, 2024',
                'Thursday, April 25, 2024',
                'Thursday, April 25, 2024',
                'Wednesday, April 24, 2024',
                'Wednesday, April 24, 2024',
                'Wednesday, April 24, 2024',
                'Tuesday, April 23, 2024',
                'Tuesday, April 23, 2024',
                'Monday, April 22, 2024',
                'Monday, April 22, 2024'
            ],
            'bo': [
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO5',
                'BO5',
                'BO3',
                'BO3',
                'BO3',
                'BO5',
                'BO5',
                'BO3',
                'BO3',
                'BO3',
                'BO5',
                'BO5',
                'BO3',
                'BO3',
                'BO3',
                'BO5',
                'BO5',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO3',
                'BO5',
                'BO5',
                'BO5',
                'BO5'
                ],
                'team_1': [
                    'T1',
                    'FLY',
                    'RAP',
                    'LGDY',
                    'OMG.A',
                    'MAX',
                    'WEA',
                    'TT.Y',
                    'FPB',
                    'IGY',
                    'WBG.Y',
                    'VKS.A',
                    'ES',
                    'TT.Y',
                    'BLGJ',
                    'TESC',
                    'ANC',
                    'PNG.A',
                    'JJH',
                    'RAP',
                    'JDM',
                    'LLL.A',
                    'BDS.A',
                    'TT.Y',
                    'IGY',
                    'MAX',
                    'PNG.A',
                    'ES',
                    'EDGY',
                    'BLGJ',
                    'WBG.Y',
                    'LNGA',
                    'JJH',
                    'TESC',
                    'KCB',
                    'ES',
                    'BDS.A',
                    'SKP'
                ],
                'team_2': [
                    'EST',
                    'PSG',
                    'WBG.Y',
                    'FPB',
                    'IGY',
                    'AL.Y',
                    'UPA',
                    'JDM',
                    'LNGA',
                    'EDGY',
                    'JJH',
                    'PNG.A',
                    'BJK',
                    'RYL',
                    'OMG.A',
                    'AL.Y',
                    'GZ',
                    'KBM.A',
                    'UPA',
                    'WEA',
                    'EDGY',
                    'KBM.A',
                    'BJK',
                    'FPB',
                    'LNGA',
                    'TESC',
                    'VKS.A',
                    'GK',
                    'OMG.A',
                    'LGDY',
                    'MJ',
                    'JDM',
                    'MAX',
                    'WEA',
                    'GK',
                    'NGX',
                    'OA',
                    'BJK'
                ],
                'score': [
                    ('2:0', ''),
                    ('2:1', ''),
                    ('0:2', ''),
                    ('1:2', ''),
                    ('0:2', ''),
                    ('2:0', ''),
                    ('0:2', ''),
                    ('2:1', ''),
                    ('1:2', ''),
                    ('0:2', ''),
                    ('2:1', ''),
                    ('1:3', ''),
                    ('3:1', ''),
                    ('1:2', ''),
                    ('1:2', ''),
                    ('2:0', ''),
                    ('1:3', ''),
                    ('3:1', ''),
                    ('1:2', ''),
                    ('1:2', ''),
                    ('0:2', ''),
                    ('0:3', ''),
                    ('2:3', ''),
                    ('0:2', ''),
                    ('2:1', ''),
                    ('0:2', ''),
                    ('1:3', ''),
                    ('3:1', ''),
                    ('2:0', ''),
                    ('2:1', ''),
                    ('2:1', ''),
                    ('0:2', ''),
                    ('0:2', ''),
                    ('2:1', ''),
                    ('2:3', ''),
                    ('3:1', ''),
                    ('3:0', ''),
                    ('2:3', '')
                ]
            }
        )
