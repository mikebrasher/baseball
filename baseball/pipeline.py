import csv
import os
import sqlite3
import time
import datetime
from baseball.player import Play, Player, parse_game_id, game_id_to_datetime


class Pipeline:

    def __init__(self):
        self.data_path = '../data'
        self.season_path = os.path.join(self.data_path, 'seasons')
        self.db_file = os.path.join(self.data_path, 'features.db')
        self.play = Play()

        self.lo_year = 1914
        self.hi_year = 2022

        # exclusive prefix sum of each player's career stats for each game they play
        self.prefix_sum = {}

        self.runners = {
            '1': 'runner_1b',
            '2': 'runner_2b',
            '3': 'runner_3b',
        }

        self.positions = {
            '1': 'pitcherID',
            '2': 'field_C_playerID',
            '3': 'field_1B_playerID',
            '4': 'field_2B_playerID',
            '5': 'field_3B_playerID',
            '6': 'field_SS_playerID',
            '7': 'field_LF_playerID',
            '8': 'field_CF_playerID',
            '9': 'field_RF_playerID',
        }

    def extract(self, year):
        if not isinstance(year, int):
            print('year {} is not an int'.format(year))
            return None
        if not (self.lo_year <= year <= self.hi_year):
            print('year {} out of range'.format(year))
            return None

        rs = os.path.join(self.season_path, '{}rs.csv'.format(year))
        print('extracting {}'.format(rs))
        with open(rs) as csv_file:
            reader = csv.DictReader(csv_file)

            data = {}
            for event in reader:
                gameID = event['gameID']
                if gameID in data:
                    data[gameID].append(event)
                else:
                    data[gameID] = [event]
        return data

    def transform(self, game_events):
        players = {}

        def add_player(p):
            if p not in players:
                players[p] = Player(p)

        def get_lineup(e):
            lineup = {
                'pitcher': e['pitcherID'],
                'catcher': e['field_C_playerID'],
                'first_base': e['field_1B_playerID'],
                'second_base': e['field_2B_playerID'],
                'third_base': e['field_3B_playerID'],
                'short_stop': e['field_SS_playerID'],
                'left_field': e['field_LF_playerID'],
                'center_field': e['field_CF_playerID'],
                'right_field': e['field_RF_playerID'],
            }
            return lineup

        vis_score = 0
        home_score = 0
        starting_lineup = {'visitor': None, 'home': None}

        max_event_in_game = 0
        for event in game_events:
            event_in_game = int(event['event_in_game'])
            if event_in_game > max_event_in_game:
                max_event_in_game = event_in_game
                vis_score = int(event['vis_score'])
                home_score = int(event['home_score'])

            # save starting lineup for first event each team is fielding
            if event['visitor_or_home'] == '0':  # 0: visitor batting, 1: home batting
                # visitor batting, home fielding
                if starting_lineup['home'] is None:
                    starting_lineup['home'] = get_lineup(event)
            else:
                # home batting, visitor fielding
                if starting_lineup['visitor'] is None:
                    starting_lineup['visitor'] = get_lineup(event)

            self.play.parse(event['theplay'], event['baserunning'])

            #  ------------ parse batting ------------
            player_id = event['batterID']
            add_player(player_id)
            players[player_id].batting.append(self.play)

            #  ------------ parse base running ------------
            for runner, label in self.runners.items():
                player_id = event[label]
                if player_id != '':
                    add_player(player_id)
                    players[player_id].base_running.append(self.play, runner)

            #  ------------ parse fielding ------------
            for position, label in self.positions.items():
                player_id = event[label]
                add_player(player_id)
                players[player_id].fielding.append(self.play, position)

            #  ------------ parse pitching ------------
            player_id = event['pitcherID']
            add_player(player_id)
            players[player_id].pitching.append(self.play)

        home_win = 1 if home_score > vis_score else 0
        game_result = {'vis_score': vis_score, 'home_score': home_score, 'result': home_win}

        return players, game_result, starting_lineup

    def load(self, connection, game_data):
        cursor = connection.cursor()

        num_feature = len(Player('foo').features())

        # reformat data to load into tables
        game_table_data = []
        player_table_data = []
        # get games in chronological order
        all_games = sorted(game_data.keys(), key=game_id_to_datetime)
        for game_id in all_games:
            players, game_result, starting_lineup = game_data[game_id]
            game_datetime = str(game_id_to_datetime(game_id))
            game_row = (
                game_id,
                game_datetime,
                game_result['vis_score'],
                game_result['home_score'],
                game_result['result'],
                starting_lineup['visitor']['pitcher'],
                starting_lineup['visitor']['catcher'],
                starting_lineup['visitor']['first_base'],
                starting_lineup['visitor']['second_base'],
                starting_lineup['visitor']['third_base'],
                starting_lineup['visitor']['short_stop'],
                starting_lineup['visitor']['left_field'],
                starting_lineup['visitor']['center_field'],
                starting_lineup['visitor']['right_field'],
                starting_lineup['home']['pitcher'],
                starting_lineup['home']['catcher'],
                starting_lineup['home']['first_base'],
                starting_lineup['home']['second_base'],
                starting_lineup['home']['third_base'],
                starting_lineup['home']['short_stop'],
                starting_lineup['home']['left_field'],
                starting_lineup['home']['center_field'],
                starting_lineup['home']['right_field'],
            )
            game_table_data.append(game_row)

            for player_id, player in players.items():
                if player_id not in self.prefix_sum:
                    self.prefix_sum[player_id] = [0] * num_feature
                player_row = [player_id, game_id, game_datetime] + self.prefix_sum[player_id]
                player_game_features = player.features()
                for idx in range(num_feature):
                    self.prefix_sum[player_id][idx] += player_game_features[idx]
                player_table_data.append(tuple(player_row))

        # create new game table if it doesn't already exist
        cmd = """
            CREATE TABLE IF NOT EXISTS
                game(
                    game_id,
                    datetime,
                    vis_score,
                    home_score,
                    result,
                    vis_catcher,
                    vis_pitcher,
                    vis_first_base,
                    vis_second_base,
                    vis_third_base,
                    vis_short_stop,
                    vis_left_field,
                    vis_center_field,
                    vis_right_field,
                    home_pitcher,
                    home_catcher,
                    home_first_base,
                    home_second_base,
                    home_third_base,
                    home_short_stop,
                    home_left_field,
                    home_center_field,
                    home_right_field
                )
        """
        cursor.execute(cmd)
        connection.commit()

        # insert result into game table
        if game_table_data:
            num_column = len(game_table_data[0])
            cmd = 'INSERT INTO game VALUES({})'.format(', '.join(['?'] * num_column))
            cursor.executemany(cmd, game_table_data)
        connection.commit()

        # create new player table listing player x game features
        num_feature = len(Player('foo').features())
        feature_header = []
        for idx in range(num_feature):
            feature_header.append('x{:03}'.format(idx))
        cmd = 'CREATE TABLE IF NOT EXISTS player(player_id, game_id, datetime, {})'.format(', '.join(feature_header))
        cursor.execute(cmd)
        connection.commit()

        # insert player x game feature into player table
        if player_table_data:
            num_column = len(player_table_data[0])
            cmd = 'INSERT INTO player VALUES({})'.format(', '.join(['?'] * num_column))
            cursor.executemany(cmd, player_table_data)
        connection.commit()

    def process(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        con = sqlite3.connect(self.db_file)

        tic = time.time()
        for year in range(self.lo_year, self.hi_year + 1):
            # extract
            raw_data = self.extract(year)

            # transform
            game_data = {}
            for game_id, game_events in raw_data.items():
                # print('transforming game: {}'.format(game_id))
                game_data[game_id] = self.transform(game_events)

            # load
            self.load(con, game_data)
        toc = time.time()
        print('processed all seasons in {} seconds'.format(toc - tic))
        # processed all seasons in 530.7778089046478 seconds

        con.close()


if __name__ == '__main__':
    p = Pipeline()
    p.lo_year = p.hi_year  # just process last year
    p.process()
