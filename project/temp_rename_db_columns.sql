/*
    Quick code to rename all column names accordingly in the database. To run in DB browser. Useful to updating a sqlite database that has the old column naming format.
*/
-- Modifying table "game"
ALTER TABLE game RENAME COLUMN gamedatetime TO game_datetime;
ALTER TABLE game RENAME COLUMN team1 TO team_1;
ALTER TABLE game RENAME COLUMN team2 TO team_2;
ALTER TABLE game RENAME COLUMN team1score TO score_team_1;
ALTER TABLE game RENAME COLUMN team2score TO score_team_2;

-- Modifying game "game_prono"
ALTER TABLE game RENAME COLUMN team1prono TO prono_team_1;
ALTER TABLE game RENAME COLUMN team2prono TO prono_team_2;

