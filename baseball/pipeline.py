import csv
from os import path
import sqlite3
from baseball.player import Play, Player


class Pipeline:

    def __init__(self, data_path='../data/seasons', db_file='features.db'):
        self.data_path = data_path
        self.db_file = db_file
        self.play = Play()

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
        if not (1914 <= year <= 2022):
            print('year {} out of range'.format(year))
            return None

        rs = path.join(self.data_path, '{}rs.csv'.format(year))
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

        vis_score = 0
        home_score = 0

        max_event_in_game = 0
        for event in game_events:
            event_in_game = int(event['event_in_game'])
            if event_in_game > max_event_in_game:
                max_event_in_game = event_in_game
                vis_score = int(event['vis_score'])
                home_score = int(event['home_score'])

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

        return players, game_result

    def load(self, connection, game_data):
        cursor = connection.cursor()

        # reformat data to load into tables
        game_table_data = []
        player_table_data = []
        for game_id, (players, game_result) in game_data.items():
            game_row = (game_id, game_result['vis_score'], game_result['home_score'], game_result['result'])
            game_table_data.append(game_row)

            for player_id, player in players.items():
                player_row = [player_id, game_id] + player.feature()
                player_table_data.append(tuple(player_row))

        # create new game table if it doesn't already exist
        cmd = 'CREATE TABLE IF NOT EXISTS game(game_id, vis_score, home_score, result)'
        cursor.execute(cmd)
        connection.commit()

        # insert result into game table
        cmd = 'INSERT INTO game VALUES(?, ?, ?, ?)'
        cursor.executemany(cmd, game_table_data)
        connection.commit()

        # create new player table listing player x game features
        num_feature = len(Player('foo').feature())
        feature_header = []
        for idx in range(num_feature):
            feature_header.append('x{:03}'.format(idx))
        cmd = 'CREATE TABLE IF NOT EXISTS player(player_id, game_id, {})'.format(', '.join(feature_header))
        cursor.execute(cmd)
        connection.commit()

        # insert player x game feature into player table
        if player_table_data:
            column_count = len(player_table_data[0])
            cmd = 'INSERT INTO player VALUES({})'.format(', '.join(['?'] * column_count))
            cursor.executemany(cmd, player_table_data)
        connection.commit()

    def process(self, year):
        con = sqlite3.connect(self.db_file)

        # extract
        raw_data = self.extract(year)

        # transform
        game_data = {}
        for game_id, game_events in raw_data.items():
            print('transforming game: {}'.format(game_id))
            players, game_result = self.transform(game_events)
            game_data[game_id] = (players, game_result)

        # load
        self.load(con, game_data)

        con.close()
