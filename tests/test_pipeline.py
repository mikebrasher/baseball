import unittest
import sqlite3
import os
from baseball.pipeline import Pipeline


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

    def test_transform(self):
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
        self.assertEqual('valdf001', starting_lineup['visitor']['pitcher'])
        self.assertEqual('maldm001', starting_lineup['visitor']['catcher'])
        self.assertEqual('gurry001', starting_lineup['visitor']['first_base'])
        self.assertEqual('altuj001', starting_lineup['visitor']['second_base'])
        self.assertEqual('brega001', starting_lineup['visitor']['third_base'])
        self.assertEqual('penaj004', starting_lineup['visitor']['short_stop'])
        self.assertEqual('alvay001', starting_lineup['visitor']['left_field'])
        self.assertEqual('mccoc001', starting_lineup['visitor']['center_field'])
        self.assertEqual('tuckk001', starting_lineup['visitor']['right_field'])
        self.assertEqual('ohtas001', starting_lineup['home']['pitcher'])
        self.assertEqual('stasm001', starting_lineup['home']['catcher'])
        self.assertEqual('walsj001', starting_lineup['home']['first_base'])
        self.assertEqual('duffm002', starting_lineup['home']['second_base'])
        self.assertEqual('renda001', starting_lineup['home']['third_base'])
        self.assertEqual('fletd002', starting_lineup['home']['short_stop'])
        self.assertEqual('adelj001', starting_lineup['home']['left_field'])
        self.assertEqual('troum001', starting_lineup['home']['center_field'])
        self.assertEqual('marsb002', starting_lineup['home']['right_field'])

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

        cmd = 'SELECT * FROM player'
        player_count = 0
        for _ in cur.execute(cmd):
            player_count += 1
        self.assertEqual(28, player_count)

        con.close()

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

        cmd = 'SELECT * FROM player'
        player_count = 0
        for _ in cur.execute(cmd):
            player_count += 1
        self.assertEqual(70894, player_count)

        # assuming all features are positive,
        # prefix sum should be monotonically increasing
        cmd = 'SELECT * FROM player WHERE player_id=? ORDER BY datetime ASC'
        player_id = 'ohtas001'
        feature_idx = 3
        prev = None
        for row in cur.execute(cmd, [player_id]):
            if prev is not None:
                for idx in range(feature_idx, len(prev)):
                    self.assertTrue(row[idx] >= prev[idx])
            prev = row

        # clean up
        con.close()
        if os.path.exists(db_file):
            os.remove(db_file)


if __name__ == '__main__':
    unittest.main()
