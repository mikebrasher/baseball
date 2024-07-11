import csv
import sqlite3
import os
import time
from baseball.player import Play, Player, game_id_to_datetime


class Pipeline:

    def __init__(self, db_name='features'):
        self.data_path = '../data'
        self.season_path = os.path.join(self.data_path, 'seasons')
        self.db_file = os.path.join(self.data_path, '{}.db'.format(db_name))
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
        print('  extracting {}'.format(rs))
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

        # potential improvement: get designate hitter
        # can be parsed from event files
        # maybe parse first nine batters in game, but could catch early substitutions
        def get_lineup(e, offset):
            lineup = {
                e['pitcherID']: 1 + offset,
                e['field_C_playerID']: 2 + offset,
                e['field_1B_playerID']: 3 + offset,
                e['field_2B_playerID']: 4 + offset,
                e['field_3B_playerID']: 5 + offset,
                e['field_SS_playerID']: 6 + offset,
                e['field_LF_playerID']: 7 + offset,
                e['field_CF_playerID']: 8 + offset,
                e['field_RF_playerID']: 9 + offset,
            }
            return lineup

        vis_score = 0
        home_score = 0

        vis_offset = -1
        home_offset = 8
        starting_lineup = {}

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
                if home_offset is not None:
                    starting_lineup.update(get_lineup(event, home_offset))
                    home_offset = None
            else:
                # home batting, visitor fielding
                if vis_offset is not None:
                    starting_lineup.update(get_lineup(event, vis_offset))
                    vis_offset = None

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
        num_player = 18
        num_aggregate_feature = num_player * num_feature

        # create new player table listing player x game features
        num_feature = len(Player('foo').features())
        feature_header = []
        for idx in range(num_aggregate_feature):
            feature_header.append('x{:04}'.format(idx))

        # reformat data to load into tables
        game_table_data = []
        # get games in chronological order to correctly calculate prefix sum
        all_games = sorted(game_data.keys(), key=game_id_to_datetime)
        for game_id in all_games:
            players, game_result, starting_lineup = game_data[game_id]
            assert len(starting_lineup) == num_player
            game_datetime = str(game_id_to_datetime(game_id))

            aggregate_features = [0] * num_aggregate_feature
            for player_id, player in players.items():
                # if player not seen yet, initialize prefix to zero
                if player_id not in self.prefix_sum:
                    self.prefix_sum[player_id] = [0] * num_feature

                # if player is in the starting line up, aggregate
                # individual player features ordered by team and position
                if player_id in starting_lineup:
                    offset = starting_lineup[player_id] * num_feature
                    aggregate_features[offset:offset + num_feature] = self.prefix_sum[player_id]

                # update the prefix sum after aggregation
                player_game_features = player.features()
                for idx in range(num_feature):
                    self.prefix_sum[player_id][idx] += player_game_features[idx]

            # store the feature and label for this game
            row = [
                game_id,
                game_datetime,
                game_result['vis_score'],
                game_result['home_score'],
                game_result['result']
            ]
            row += aggregate_features
            game_table_data.append(tuple(row))

        # create new game table if it doesn't already exist
        cmd = """
            CREATE TABLE IF NOT EXISTS
                game(
                    game_id,
                    datetime,
                    vis_score,
                    home_score,
                    result,
                    {}
                )
        """.format(',\n'.join(feature_header))
        cursor.execute(cmd)
        connection.commit()

        # insert result into game table
        if game_table_data:
            num_column = len(game_table_data[0])
            cmd = 'INSERT INTO game VALUES({})'.format(', '.join(['?'] * num_column))
            cursor.executemany(cmd, game_table_data)
        connection.commit()

    def process(self):
        if os.path.exists(self.db_file):
            print('file {} already exists'.format(self.db_file))
            return

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
        print('  processed all seasons in {} seconds'.format(toc - tic))

        con.close()


if __name__ == '__main__':
    print('generating train database...')
    train_pipe = Pipeline('train')
    train_pipe.hi_year = 2020
    train_pipe.process()

    print('generating valid database...')
    valid_pipe = Pipeline('valid')
    valid_pipe.lo_year = valid_pipe.hi_year = 2021
    valid_pipe.process()

    print('generating test database...')
    test_pipe = Pipeline('test')
    test_pipe.lo_year = test_pipe.hi_year = 2022
    test_pipe.process()
