import unittest
import sqlite3
import os
import numpy as np
from baseball.pipeline import Pipeline, StandardScaler


class TestStandardScaler(unittest.TestCase):

    def setUp(self):
        self.num_sample = 5
        self.num_feature = 3
        self.scaler = StandardScaler(num_feature=self.num_feature)
        self.rng = np.random.default_rng(12345)

    def test_update(self):
        x = self.rng.random((self.num_sample, self.num_feature))

        old_sum1 = self.scaler.sum1.copy()
        old_sum2 = self.scaler.sum2.copy()
        for sample in x:
            self.scaler.update(list(sample))
            for idx in range(self.num_feature):
                self.assertAlmostEqual(sample[idx], self.scaler.sum1[idx] - old_sum1[idx])
                self.assertAlmostEqual(sample[idx] * sample[idx], self.scaler.sum2[idx] - old_sum2[idx])
            old_sum1 = self.scaler.sum1.copy()
            old_sum2 = self.scaler.sum2.copy()

    def test_calculate(self):
        x = self.rng.random((self.num_sample, self.num_feature))
        expected_mu = x.mean(axis=0)
        expected_std = x.std(axis=0)

        for sample in x:
            self.scaler.update(list(sample))

        actual_mu, actual_std = self.scaler.calculate_statistics()

        for idx in range(self.num_feature):
            self.assertAlmostEqual(expected_mu[idx], actual_mu[idx])
            self.assertAlmostEqual(expected_std[idx], actual_std[idx])


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = Pipeline()

    def test_extract_not_int(self):
        result = self.pipeline.extract('foo')
        self.assertIsNone(result)

    def test_extract_out_of_bounds(self):
        result = self.pipeline.extract(1900)
        self.assertIsNone(result)

        result = self.pipeline.extract(2050)
        self.assertIsNone(result)

    def test_extract_num_games(self):
        result = self.pipeline.extract(2022)
        self.assertEqual(2430, len(result))

    def test_transform_angels_april_07_2022(self):
        data = self.pipeline.extract(2022)
        gameID = 'ANA202204070'
        game = data[gameID]

        players, game_result, starting_lineup = self.pipeline.transform(game)

        self.assertEqual(28, len(players))

        # test some batting stats
        self.assertEqual(4, players['mccoc001'].batting.at_bat)
        self.assertEqual(2, players['mccoc001'].batting.hit)

        # test some base running stats
        self.assertEqual(1, players['brega001'].base_running.advance12)
        self.assertEqual(1, players['branm003'].base_running.score_from_second)

        # test some fielding stats
        self.assertEqual(4, players['fletd002'].fielding.assist)
        self.assertAlmostEqual(9.0, players['fletd002'].fielding.inning_at_position)

        # test some pitching stats
        self.assertEqual(4, players['ohtas001'].pitching.hit)
        self.assertEqual(9, players['ohtas001'].pitching.strike_out)
        self.assertAlmostEqual(14/3, players['ohtas001'].pitching.innings_pitched)

        self.assertEqual(3, game_result['vis_score'])
        self.assertEqual(1, game_result['home_score'])
        self.assertEqual(0, game_result['result'])

        # test starting lineup
        expected = {
            'valdf001': 0,
            'maldm001': 1,
            'gurry001': 2,
            'altuj001': 3,
            'brega001': 4,
            'penaj004': 5,
            'alvay001': 6,
            'mccoc001': 7,
            'tuckk001': 8,
            'ohtas001': 9,
            'stasm001': 10,
            'walsj001': 11,
            'duffm002': 12,
            'renda001': 13,
            'fletd002': 14,
            'adelj001': 15,
            'troum001': 16,
            'marsb002': 17,
        }
        self.assertDictEqual(expected, starting_lineup)

    def test_transform_walk_off(self):
        data = self.pipeline.extract(2022)
        # dodgers @ padres 4/23/2022
        gameID = 'SDN202204230'
        game = data[gameID]

        _, game_result, _ = self.pipeline.transform(game)

        self.assertEqual(2, game_result['vis_score'])
        self.assertEqual(3, game_result['home_score'])
        self.assertEqual(1, game_result['result'])

    def test_transform_game_result(self):
        data = self.pipeline.extract(2022)

        dodgers = 'LAN'

        home_win = 0
        home_loss = 0
        away_win = 0
        away_loss = 0
        for gameID in data:
            game = data[gameID]
            _, game_result, _ = self.pipeline.transform(game)
            if game[0]['hometeam'] == dodgers:
                if game_result['result'] == 1:
                    home_win += 1
                else:
                    home_loss += 1
            elif game[0]['visteam'] == dodgers:
                if game_result['result'] == 1:
                    away_loss += 1
                else:
                    away_win += 1

        self.assertEqual(57, home_win)
        self.assertEqual(24, home_loss)
        self.assertEqual(54, away_win)
        self.assertEqual(27, away_loss)

        self.assertEqual(111, home_win + away_win)
        self.assertEqual(51, home_loss + away_loss)

    def test_load(self):
        # connect to database and get cursor
        con = sqlite3.connect(':memory:')
        cur = con.cursor()

        data = self.pipeline.extract(2022)
        game_id = 'ANA202204070'
        game = data[game_id]
        players, game_result, starting_lineup = self.pipeline.transform(game)
        game_data = {game_id: (players, game_result, starting_lineup)}

        self.pipeline.load(con, game_data)

        cmd = 'SELECT * FROM game'
        game_count = 0
        for _ in cur.execute(cmd):
            game_count += 1
        self.assertEqual(1, game_count)

    def test_publish(self):
        # connect to database and get cursor
        con = sqlite3.connect(':memory:')
        cur = con.cursor()

        num_sample = 5
        data = []
        for offset in range(num_sample):
            sample = [offset + idx for idx in range(self.pipeline.num_aggregate_feature)]
            data.append(sample)
            self.pipeline.scaler.update(sample)

        data = np.array(data)
        expected_mu = data.mean(axis=0)
        expected_std = data.std(axis=0)

        self.pipeline.publish(con)

        cmd = """SELECT * FROM scaler WHERE statistic='mu'"""
        row = cur.execute(cmd).fetchone()
        self.assertEqual(0, row[0])
        self.assertEqual('mu', row[1])
        actual_mu = row[2:]

        cmd = """SELECT * FROM scaler WHERE statistic='std'"""
        row = cur.execute(cmd).fetchone()
        self.assertEqual(1, row[0])
        self.assertEqual('std', row[1])
        actual_std = row[2:]

        for idx in range(self.pipeline.num_aggregate_feature):
            self.assertAlmostEqual(expected_mu[idx], actual_mu[idx])
            self.assertAlmostEqual(expected_std[idx], actual_std[idx])

    def test_process(self):
        db_file = 'test_process.db'
        if os.path.exists(db_file):
            os.remove(db_file)

        self.pipeline.db_file = db_file
        self.pipeline.lo_year = self.pipeline.hi_year = 2022  # just process 2022
        self.pipeline.process()

        # connect to database and get cursor
        con = sqlite3.connect(db_file)
        cur = con.cursor()

        cmd = 'SELECT * FROM game'
        game_count = 0
        for _ in cur.execute(cmd):
            game_count += 1
        self.assertEqual(2430, game_count)

        # clean up
        con.close()
        if os.path.exists(db_file):
            os.remove(db_file)


if __name__ == '__main__':
    unittest.main()
