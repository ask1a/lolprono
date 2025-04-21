import json
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
    data = {'id': [3, 4], 'leaguename': ['Mid-Season Invitational 2024', 'LEC Spring 2025']}
    # Declaring class
    test_panda = utils.PandaScoreRequest(test_job=True)
    test_panda.leagues = pd.DataFrame(data)
    # Test case 1 : corresponding
    assert test_panda.assign_league_id('LEC spring 2024') == -1
    # Test case 2 : partial
    assert test_panda.assign_league_id('Mid-Season Invitational 2024') == 3
    # Test case 2bis : barely correspond
    assert test_panda.assign_league_id('MSI 202') == -1
    # Test case 3 : no match
    assert test_panda.assign_league_id('LCK 2024') == -1
    # Test case 4 : empty
    assert test_panda.assign_league_id('') == -1
    # Test case 5 : doesnt exist
    assert test_panda.assign_league_id('MLS') == -1


def test_identifty_team_names(expected_df_for_clean_schedule):
    test_panda = utils.PandaScoreRequest(test_job=True)
    test_df = pd.DataFrame(
        {
            'leagueid': [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
            'bo': [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
            'game_datetime': ['2025-04-20 15:00:00', '2025-04-20 17:00:00', '2025-04-21 15:00:00', '2025-04-21 17:00:00',
                '2025-04-26 13:00:00', '2025-04-26 15:00:00', '2025-04-27 13:00:00', '2025-04-27 15:00:00',
                '2025-04-28 15:00:00', '2025-04-28 17:00:00', '2025-05-03 15:00:00', '2025-05-03 17:00:00',
                '2025-05-04 15:00:00', '2025-05-04 17:00:00', '2025-05-05 15:00:00', '2025-05-05 17:00:00',
                '2025-05-10 15:00:00', '2025-05-10 17:00:00', '2025-05-11 15:00:00', '2025-05-11 17:00:00',
                '2025-05-12 15:00:00', '2025-05-12 17:00:00'],
            'team_1': [
                    'TH', 'G2', 'SK', 'MKOI', 'G2', 'MKOI', 'G2', 'MKOI', 'TH', "VIT",
                    'FNC', 'KC', 'GX', 'G2', 'TH', 'MKOI', 'G2', 'KC', 'VIT', 'KC', 'TH', 'MKOI'
                ],
            'team_2': [
                    'VIT', 'BDS', 'RGE', 'VIT', 'GX', 'FNC', 'FNC', 'GX', 'SK', 'BDS', 'BDS', 'RGE',
                    'BDS', 'VIT', 'FNC', 'SK', 'SK', 'VIT', 'SK', 'G2', 'GX', 'RGE'
                ]
        }
    )
    test_df = test_panda.identifty_team_names(test_df)
    assert_frame_equal(test_df.reset_index(drop=True), expected_df_for_clean_schedule.reset_index(drop=True), check_dtype=False)


def test_get_game_schedule_dataframe(json_content_schedule, expected_df_for_get_game_schedule_dataframe):
    test_panda = utils.PandaScoreRequest(test_job=True)
    rslt_df = test_panda.get_upcoming_games('LEC', test_json=json_content_schedule)
    expected_df = expected_df_for_get_game_schedule_dataframe
    expected_df['game_datetime'] = pd.to_datetime(expected_df['game_datetime']).dt.date
    rslt_df['game_datetime'] = pd.to_datetime(rslt_df['game_datetime']).dt.date
    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_clean_schedule(expected_df_for_get_game_schedule_dataframe,expected_df_for_clean_schedule):
    test_panda = utils.PandaScoreRequest(test_job=True)
    rslt_df = test_panda.clean_schedule(expected_df_for_get_game_schedule_dataframe)
    expected_df = expected_df_for_clean_schedule
    expected_df['game_datetime'] = pd.to_datetime(expected_df['game_datetime']).dt.date
    rslt_df['game_datetime'] = pd.to_datetime(rslt_df['game_datetime']).dt.date

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_clean_results(expected_df_for_get_game_results_dataframe, expected_df_for_clean_results):
    test_panda = utils.PandaScoreRequest(test_job=True)
    rslt_df = test_panda.clean_results(expected_df_for_get_game_results_dataframe)
    print(rslt_df)
    expected_df = expected_df_for_clean_results
    print(expected_df)

    assert_frame_equal(rslt_df.reset_index(drop=True), expected_df.reset_index(drop=True), check_dtype=False)


def test_get_game_results_dataframe(json_content_results, expected_df_for_get_game_results_dataframe):
    test_panda = utils.PandaScoreRequest(test_job=True)
    results_df = test_panda.get_past_games('LEC', test_json=json_content_results)
    results_expected_df = expected_df_for_get_game_results_dataframe
    results_df['game_date'] = pd.to_datetime(results_df['game_date']).dt.date
    results_expected_df['game_date'] = pd.to_datetime(results_expected_df['game_date']).dt.date
    assert_frame_equal(results_df.reset_index(drop=True), results_expected_df.reset_index(drop=True), check_dtype=False)


@pytest.fixture
def json_content_schedule():
    home = Path(__file__).resolve().parent.parent.parent
    file_path = home / 'jobs/test/upcoming.json'
    with open(file_path, "rb") as f:
        json_content_byte = json.load(f)
    return json_content_byte

@pytest.fixture
def json_content_results():
    home = Path(__file__).resolve().parent.parent.parent
    file_path = home / 'jobs/test/past.json'
    with open(file_path, "rb") as f:
        json_content_byte = json.load(f)
    return json_content_byte

@pytest.fixture
def expected_df_for_clean_schedule():
    return pd.DataFrame(
        {
            'leagueid': [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
            'bo': [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
            'game_datetime': ['2025-04-20 15:00:00', '2025-04-20 17:00:00', '2025-04-21 15:00:00', '2025-04-21 17:00:00',
                '2025-04-26 13:00:00', '2025-04-26 15:00:00', '2025-04-27 13:00:00', '2025-04-27 15:00:00',
                '2025-04-28 15:00:00', '2025-04-28 17:00:00', '2025-05-03 15:00:00', '2025-05-03 17:00:00',
                '2025-05-04 15:00:00', '2025-05-04 17:00:00', '2025-05-05 15:00:00', '2025-05-05 17:00:00',
                '2025-05-10 15:00:00', '2025-05-10 17:00:00', '2025-05-11 15:00:00', '2025-05-11 17:00:00',
                '2025-05-12 15:00:00', '2025-05-12 17:00:00'],
            'team_1':[
                    'Team Heretics', 'G2 Esport', 'SK Gaming', 'Movistar KOI', 'G2 Esport', 'Movistar KOI', 'G2 Esport', 'Movistar KOI',
                    'Team Heretics', "Vitality", 'Fnatic', 'Karmine Corp', 'Giant X', 'G2 Esport', 'Team Heretics', 'Movistar KOI', 'G2 Esport',
                    'Karmine Corp', 'Vitality', 'Karmine Corp', 'Team Heretics', 'Movistar KOI'
                ],
            'team_2':  [
                    'Vitality', 'Team BDS', 'Rogue', 'Vitality', 'Giant X', 'Fnatic', 'Fnatic', 'Giant X', 'SK Gaming', 'Team BDS', 'Team BDS', 'Rogue',
                    'Team BDS', 'Vitality', 'Fnatic', 'SK Gaming', 'SK Gaming', 'Vitality', 'SK Gaming', 'G2 Esport', 'Giant X', 'Rogue'
                ]
        }
    )


@pytest.fixture
def expected_df_for_clean_results():
    return pd.DataFrame(
        {
            'leagueid': [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
            'bo': [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
            'game_date': [
                '2025-04-20', '2025-04-20', '2025-04-21', '2025-04-21',
                '2025-04-26', '2025-04-26', '2025-04-27', '2025-04-27',
                '2025-04-28', '2025-04-28', '2025-05-03', '2025-05-03',
                '2025-05-04', '2025-05-04', '2025-05-05', '2025-05-05',
                '2025-05-10', '2025-05-10', '2025-05-11', '2025-05-11',
                '2025-05-12', '2025-05-12'],
            'team_1':[
                    'Team Heretics', 'G2 Esport', 'SK Gaming', 'Movistar KOI', 'G2 Esport', 'Movistar KOI', 'G2 Esport', 'Movistar KOI',
                    'Team Heretics', "Vitality", 'Fnatic', 'Karmine Corp', 'Giant X', 'G2 Esport', 'Team Heretics', 'Movistar KOI', 'G2 Esport',
                    'Karmine Corp', 'Vitality', 'Karmine Corp', 'Team Heretics', 'Movistar KOI'
                ],
            'team_2':  [
                    'Vitality', 'Team BDS', 'Rogue', 'Vitality', 'Giant X', 'Fnatic', 'Fnatic', 'Giant X', 'SK Gaming', 'Team BDS', 'Team BDS', 'Rogue',
                    'Team BDS', 'Vitality', 'Fnatic', 'SK Gaming', 'SK Gaming', 'Vitality', 'SK Gaming', 'G2 Esport', 'Giant X', 'Rogue'
                ],
            'score_team_1': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ],
            'score_team_2': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]
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
            'game_datetime': [
                    '2025-04-20 15:00:00', '2025-04-20 17:00:00',
                    '2025-04-21 15:00:00', '2025-04-21 17:00:00',
                    '2025-04-26 13:00:00', '2025-04-26 15:00:00',
                    '2025-04-27 13:00:00', '2025-04-27 15:00:00',
                    '2025-04-28 15:00:00', '2025-04-28 17:00:00',
                    '2025-05-03 15:00:00', '2025-05-03 17:00:00',
                    '2025-05-04 15:00:00', '2025-05-04 17:00:00',
                    '2025-05-05 15:00:00', '2025-05-05 17:00:00',
                    '2025-05-10 15:00:00', '2025-05-10 17:00:00',
                    '2025-05-11 15:00:00', '2025-05-11 17:00:00',
                    '2025-05-12 15:00:00', '2025-05-12 17:00:00'
                ],
            'bo': [
                    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
                ],
            'team_1': [
                    'TH', 'G2', 'SK', 'MKOI', 'G2', 'MKOI', 'G2', 'MKOI', 'TH', "VIT",
                    'FNC', 'KC', 'GX', 'G2', 'TH', 'MKOI', 'G2', 'KC', 'VIT', 'KC', 'TH', 'MKOI'
                ],
            'team_2': [
                    'VIT', 'BDS', 'RGE', 'VIT', 'GX', 'FNC', 'FNC', 'GX', 'SK', 'BDS', 'BDS', 'RGE',
                    'BDS', 'VIT', 'FNC', 'SK', 'SK', 'VIT', 'SK', 'G2', 'GX', 'RGE'
                ]
            }
        )

@pytest.fixture
def expected_df_for_get_game_results_dataframe():
    return pd.DataFrame(
        {
            'league_name':[
                'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025',
                'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025',
                'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025',
                'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025', 'LEC Spring 2025'
            ],
            'game_date': [
                '2025-04-20', '2025-04-20', '2025-04-21', '2025-04-21',
                '2025-04-26', '2025-04-26', '2025-04-27', '2025-04-27',
                '2025-04-28', '2025-04-28', '2025-05-03', '2025-05-03',
                '2025-05-04', '2025-05-04', '2025-05-05', '2025-05-05',
                '2025-05-10', '2025-05-10', '2025-05-11', '2025-05-11',
                '2025-05-12', '2025-05-12'
            ],
            'bo': [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            'team_1': [
                'TH', 'G2', 'SK', 'MKOI', 'G2', 'MKOI', 'G2', 'MKOI', 'TH', 'VIT', 'FNC',
                'KC', 'GX', 'G2', 'TH', 'MKOI', 'G2', 'KC', 'VIT', 'KC', 'TH', 'MKOI'
            ],
            'team_2': [
                'VIT', 'BDS', 'RGE', 'VIT', 'GX', 'FNC', 'FNC', 'GX', 'SK', 'BDS',
                'BDS', 'RGE', 'BDS', 'VIT', 'FNC', 'SK', 'SK', 'VIT', 'SK', 'G2', 'GX', 'RGE'
            ],
            'score_team_1': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ],
            'score_team_2': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ]
        }
    )
