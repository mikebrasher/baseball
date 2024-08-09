import csv
import sqlite3
import os
import time
import collections
import numpy as np
from baseball.player import Play, Player, game_id_to_datetime


class StandardScaler:
    def __init__(self, num_feature=0):
        self.num_feature = num_feature
        self.count = 0
        self.sum1 = np.zeros(num_feature)
        self.sum2 = np.zeros(num_feature)

    def update(self, x):
        x = np.array(x)
        self.sum1 += x
        self.sum2 += x * x
        self.count += 1

    def calculate_statistics(self):
        if self.count > 0:
            mu = self.sum1 / self.count
            std = np.sqrt(self.sum2 / self.count - mu * mu)
            tol = 1e-8
            invalid = std < tol
            std[invalid] = 1.0
        else:
            mu = np.zeros(self.num_feature)
            std = np.ones(self.num_feature)
        return mu, std


runner_map = {
    '1': 'runner_1b',
    '2': 'runner_2b',
    '3': 'runner_3b',
}

position_map = {
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


class Lineup:
    def __init__(self, use_dh=False):
        self.use_dh = use_dh
        self.fielders = {}
        self.batters = []
        self.pitchers = {}
        self.designated_hitter = None
        self.team_key = None

    def reset(self):
        self.fielders = {}
        self.batters = []
        self.pitchers = {}
        self.designated_hitter = None
        self.team_key = None

    def find_designated_hitter(self):
        if self.use_dh:
            for batter_id in self.batters:
                if batter_id not in self.fielders.values():
                    self.designated_hitter = batter_id
                    break

    def relief_pitchers(self):
        result = []
        starting_pitcher = self.fielders['pitcherID']
        for pitcher in self.pitchers:
            if pitcher != starting_pitcher:
                result.append(pitcher)
        return result

    def fetch(self):
        result = [
            self.fielders['pitcherID'],
            self.fielders['field_C_playerID'],
            self.fielders['field_1B_playerID'],
            self.fielders['field_2B_playerID'],
            self.fielders['field_3B_playerID'],
            self.fielders['field_SS_playerID'],
            self.fielders['field_LF_playerID'],
            self.fielders['field_CF_playerID'],
            self.fielders['field_RF_playerID'],
        ]
        if self.use_dh:
            result.append(self.designated_hitter)
        return result


class LineupParser:
    def __init__(self, use_dh=False, use_bullpen=False):
        self.use_dh = use_dh
        self.use_bullpen = use_bullpen

        self.num_batter = 9
        self.num_bullpen = 5

        self.home = Lineup(use_dh)
        self.visitor = Lineup(use_dh)

        self.bullpen = {}  # rolling window of previous pitchers for each team

    def reset(self):
        self.home.reset()
        self.visitor.reset()

    def roster_size(self):
        result = self.num_batter
        if self.use_dh:
            result += 1
        if self.use_bullpen:
            result += self.num_bullpen
        return result

    def update_bullpen(self, team_key, pitchers):
        if self.use_bullpen:
            if team_key not in self.bullpen:
                self.bullpen[team_key] = collections.deque(maxlen=self.num_bullpen)
            for pitcher_id in pitchers:
                self.bullpen[team_key].append(pitcher_id)

    def get_bullpen(self, team_key):
        # always return a list of length num_bullpen
        result = [None] * self.num_bullpen
        if self.use_bullpen and team_key in self.bullpen:
            for idx, pitcher_id in enumerate(self.bullpen[team_key]):
                result[idx] = pitcher_id
        return result

    def append(self, event):
        self.visitor.team_key = event['visteam']
        self.home.team_key = event['hometeam']

        batter_id = event['batterID']
        pitcher_id = event['pitcherID']

        visitor_batting = event['visitor_or_home'] == '0'
        if visitor_batting:
            if len(self.visitor.batters) < self.num_batter:
                self.visitor.batters.append(batter_id)
            if not self.home.fielders:
                for position in position_map.values():
                    self.home.fielders[position] = event[position]
            self.home.pitchers[pitcher_id] = True
        else:
            if len(self.home.batters) < self.num_batter:
                self.home.batters.append(batter_id)
            if not self.visitor.fielders:
                for position in position_map.values():
                    self.visitor.fielders[position] = event[position]
            self.visitor.pitchers[pitcher_id] = True

    def fetch(self):
        if self.use_dh:
            self.home.find_designated_hitter()
            self.visitor.find_designated_hitter()

        home_lineup = self.home.fetch()
        visitor_lineup = self.visitor.fetch()

        if self.use_bullpen:
            # get previous bullpens before updating
            visitor_bullpen = self.get_bullpen(self.visitor.team_key)
            home_bullpen = self.get_bullpen(self.home.team_key)
            starting_lineup = visitor_lineup + visitor_bullpen + home_lineup + home_bullpen
            self.update_bullpen(self.home.team_key, self.home.relief_pitchers())
            self.update_bullpen(self.visitor.team_key, self.visitor.relief_pitchers())
        else:
            starting_lineup = visitor_lineup + home_lineup

        result = {player_id: idx for idx, player_id in enumerate(starting_lineup) if player_id is not None}
        return result


class Pipeline:
    def __init__(self, db_name='features', use_dh=False, use_bullpen=False):
        self.data_path = '../data'
        self.season_path = os.path.join(self.data_path, 'seasons')
        self.db_file = os.path.join(self.data_path, '{}.db'.format(db_name))
        self.play = Play()

        self.lo_year = 1914
        self.hi_year = 2022

        # exclusive prefix sum of each player's career stats for each game they play
        self.prefix_sum = {}

        self.lineup_parser = LineupParser(use_dh=use_dh, use_bullpen=use_bullpen)
        self.num_player = 2 * self.lineup_parser.roster_size()

        self.num_feature = len(Player('foo').features())
        self.num_aggregate_feature = self.num_player * self.num_feature

        # create new player table listing player x game features
        self.feature_header = []
        for idx in range(self.num_aggregate_feature):
            self.feature_header.append('x{:04}'.format(idx))

        self.scaler = StandardScaler(num_feature=self.num_aggregate_feature)

    def parse_lineup(self):
        pass

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
        players = {}  # all players active this game

        def add_player(p):
            if p not in players:
                players[p] = Player(p)

        vis_score = 0
        home_score = 0

        self.lineup_parser.reset()
        for event in game_events:
            self.lineup_parser.append(event)

            # ------------ parse the play ------------
            self.play.parse(event['theplay'], event['baserunning'])
            num_run_scored = len(self.play.score)
            visitor_batting = event['visitor_or_home'] == '0'
            if visitor_batting:
                vis_score += num_run_scored
            else:
                home_score += num_run_scored

            #  ------------ parse batting ------------
            batter_id = event['batterID']
            add_player(batter_id)
            players[batter_id].batting.append(self.play)

            #  ------------ parse base running ------------
            for runner, label in runner_map.items():
                runner_id = event[label]
                if runner_id != '':
                    add_player(runner_id)
                    players[runner_id].base_running.append(self.play, runner)

            #  ------------ parse fielding ------------
            for position, label in position_map.items():
                fielder_id = event[label]
                add_player(fielder_id)
                players[fielder_id].fielding.append(self.play, position)

            #  ------------ parse pitching ------------
            pitcher_id = event['pitcherID']
            add_player(pitcher_id)
            players[pitcher_id].pitching.append(self.play)

        home_win = 1 if home_score > vis_score else 0
        game_result = {'vis_score': vis_score, 'home_score': home_score, 'result': home_win}

        #  ------------ build starting lineup ------------
        starting_lineup = self.lineup_parser.fetch()

        return players, game_result, starting_lineup

    def load(self, connection, game_data):
        cursor = connection.cursor()

        # reformat data to load into tables
        game_table_data = []
        # get games in chronological order to correctly calculate prefix sum
        all_games = sorted(game_data.keys(), key=game_id_to_datetime)
        for game_id in all_games:
            players, game_result, starting_lineup = game_data[game_id]
            assert len(starting_lineup) == self.num_player
            game_datetime = str(game_id_to_datetime(game_id))

            # aggregate individual player features ordered by team and position
            # any expected players missing from lineup have features initialized as zeros
            aggregate_features = [0] * self.num_aggregate_feature
            for player_id in starting_lineup:
                if player_id in self.prefix_sum:
                    offset = starting_lineup[player_id] * self.num_feature
                    aggregate_features[offset:offset + self.num_feature] = self.prefix_sum[player_id]
                else:
                    # leave players spot in aggregate feature as zeros if we haven't seen them yet
                    pass
            self.scaler.update(aggregate_features)

            # update the prefix sum after aggregation
            for player_id, player in players.items():
                # if player not seen yet, initialize prefix to zero
                if player_id not in self.prefix_sum:
                    self.prefix_sum[player_id] = [0] * self.num_feature

                player_game_features = player.features()
                for idx in range(self.num_feature):
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
                    game_id PRIMARY KEY,
                    datetime,
                    vis_score,
                    home_score,
                    result,
                    {}
                )
        """.format(',\n'.join(self.feature_header))
        cursor.execute(cmd)
        connection.commit()

        # insert result into game table
        if game_table_data:
            num_column = len(game_table_data[0])
            cmd = 'INSERT INTO game VALUES({})'.format(', '.join(['?'] * num_column))
            cursor.executemany(cmd, game_table_data)
        connection.commit()

    def publish(self, connection):
        cursor = connection.cursor()

        # create new scaler table if it doesn't already exist
        cmd = """
            CREATE TABLE IF NOT EXISTS
                scaler(
                    id PRIMARY KEY,
                    statistic,
                    {}
                )
        """.format(',\n'.join(self.feature_header))
        cursor.execute(cmd)
        connection.commit()

        # insert result into scaler table
        mu, std = self.scaler.calculate_statistics()
        scaler_table_data = [
            tuple([0, 'mu'] + list(mu)),
            tuple([1, 'std'] + list(std))
        ]
        num_column = len(scaler_table_data[0])
        cmd = 'INSERT INTO scaler VALUES({})'.format(', '.join(['?'] * num_column))
        cursor.executemany(cmd, scaler_table_data)
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

        # publish
        self.publish(con)

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
