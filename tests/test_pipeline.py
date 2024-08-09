import collections
import unittest
import sqlite3
import os
import numpy as np
from baseball.pipeline import StandardScaler, Lineup, LineupParser, Pipeline


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


class TestLineup(unittest.TestCase):

    def setUp(self):
        self.lineup = Lineup()

    def test_reset(self):
        self.lineup.fielders['foo'] = 3
        self.lineup.batters.append('bar')
        self.lineup.pitchers['baz'] = 7
        self.lineup.designated_hitter = 'asdf'
        self.lineup.team_key = 'FOO'

        self.lineup.reset()

        self.assertFalse(self.lineup.fielders)
        self.assertFalse(self.lineup.batters)
        self.assertFalse(self.lineup.pitchers)
        self.assertIsNone(self.lineup.designated_hitter)
        self.assertIsNone(self.lineup.team_key)

    def test_find_designated_hitter(self):
        self.lineup.use_dh = True
        self.lineup.fielders = {
            'pitcherID': 'pitcher',
            'field_C_playerID': 'bat07',
            'field_1B_playerID': 'bat06',
            'field_2B_playerID': 'bat05',
            'field_3B_playerID': 'bat04',
            'field_SS_playerID': 'bat03',
            'field_LF_playerID': 'bat02',
            'field_CF_playerID': 'bat01',
            'field_RF_playerID': 'bat00',
        }
        self.lineup.batters = ['bat00', 'bat01', 'bat02', 'bat03', 'bat04', 'bat05', 'bat06', 'bat07', 'dh']

        self.lineup.find_designated_hitter()
        self.assertEqual('dh', self.lineup.designated_hitter)

    def test_find_designated_hitter_ohtani(self):
        # use dh is true, but pitcher bats (Ohtani rule)
        self.lineup.use_dh = True
        self.lineup.fielders = {
            'pitcherID': 'ohtas001',
            'field_C_playerID': 'bat07',
            'field_1B_playerID': 'bat06',
            'field_2B_playerID': 'bat05',
            'field_3B_playerID': 'bat04',
            'field_SS_playerID': 'bat03',
            'field_LF_playerID': 'bat02',
            'field_CF_playerID': 'bat01',
            'field_RF_playerID': 'bat00',
        }
        self.lineup.batters = ['bat00', 'bat01', 'bat02', 'bat03', 'bat04', 'bat05', 'bat06', 'bat07', 'ohtas001']

        self.lineup.find_designated_hitter()
        self.assertIsNone(self.lineup.designated_hitter)

    def test_relief_pitchers(self):
        self.lineup.fielders = {
            'pitcherID': 'starter',
        }
        self.lineup.pitchers = {'starter': True, 'relief00': True, 'relief01': True, 'relief02': True}

        expected = ['relief00', 'relief01', 'relief02']
        self.assertListEqual(expected, self.lineup.relief_pitchers())

    def test_fetch(self):
        self.lineup.fielders = {
            'pitcherID': 'pitcher',
            'field_C_playerID': 'catcher',
            'field_1B_playerID': 'first',
            'field_2B_playerID': 'second',
            'field_3B_playerID': 'third',
            'field_SS_playerID': 'short',
            'field_LF_playerID': 'left',
            'field_CF_playerID': 'center',
            'field_RF_playerID': 'right',
        }

        expected = [
            'pitcher',
            'catcher',
            'first',
            'second',
            'third',
            'short',
            'left',
            'center',
            'right',
        ]
        self.assertListEqual(expected, self.lineup.fetch())

    def test_fetch_use_dh(self):
        self.lineup.use_dh = True
        self.lineup.fielders = {
            'pitcherID': 'pitcher',
            'field_C_playerID': 'catcher',
            'field_1B_playerID': 'first',
            'field_2B_playerID': 'second',
            'field_3B_playerID': 'third',
            'field_SS_playerID': 'short',
            'field_LF_playerID': 'left',
            'field_CF_playerID': 'center',
            'field_RF_playerID': 'right',
        }

        expected = [
            'pitcher',
            'catcher',
            'first',
            'second',
            'third',
            'short',
            'left',
            'center',
            'right',
            None,
        ]
        self.assertListEqual(expected, self.lineup.fetch())

        self.lineup.designated_hitter = 'dh'
        expected[-1] = 'dh'
        self.assertListEqual(expected, self.lineup.fetch())


class TestLineupParser(unittest.TestCase):

    def setUp(self):
        self.parser = LineupParser()

    def test_reset(self):
        self.parser.home.fielders['foo'] = 3
        self.parser.home.batters.append('bar')
        self.parser.home.pitchers['baz'] = 7
        self.parser.home.designated_hitter = 'asdf'
        self.parser.home.team_key = 'FOO'

        self.parser.visitor.fielders['foo'] = 3
        self.parser.visitor.batters.append('bar')
        self.parser.visitor.pitchers['baz'] = 7
        self.parser.visitor.designated_hitter = 'asdf'
        self.parser.visitor.team_key = 'BAR'

        self.parser.reset()

        self.assertFalse(self.parser.home.fielders)
        self.assertFalse(self.parser.home.batters)
        self.assertFalse(self.parser.home.pitchers)
        self.assertIsNone(self.parser.home.designated_hitter)
        self.assertIsNone(self.parser.home.team_key)

        self.assertFalse(self.parser.visitor.fielders)
        self.assertFalse(self.parser.visitor.batters)
        self.assertFalse(self.parser.visitor.pitchers)
        self.assertIsNone(self.parser.visitor.designated_hitter)
        self.assertIsNone(self.parser.visitor.team_key)

    def test_roster_size(self):
        expected = self.parser.num_batter
        self.assertEqual(expected, self.parser.roster_size())

        use_dh = LineupParser(use_dh=True)
        expected = use_dh.num_batter + 1
        self.assertEqual(expected, use_dh.roster_size())

        use_bullpen = LineupParser(use_bullpen=True)
        expected = use_bullpen.num_batter + use_bullpen.num_bullpen
        self.assertEqual(expected, use_bullpen.roster_size())

        use_both = LineupParser(use_dh=True, use_bullpen=True)
        expected = use_both.num_batter + 1 + use_both.num_bullpen
        self.assertEqual(expected, use_both.roster_size())

    def test_update_bullpen_use_bullpen_false(self):
        self.parser.use_bullpen = False
        team_key = 'FOO'
        pitchers = ['pitch00', 'pitch01', 'pitch02']
        self.parser.update_bullpen(team_key, pitchers)
        self.assertNotIn(team_key, self.parser.bullpen)

    def test_update_bullpen(self):
        self.parser.use_bullpen = True
        team_key = 'FOO'
        pitchers = ['pitch00', 'pitch01', 'pitch02']
        self.parser.update_bullpen(team_key, pitchers)
        self.assertIn(team_key, self.parser.bullpen)
        self.assertEqual(pitchers, list(self.parser.bullpen[team_key]))

    def test_update_bullpen_wrap(self):
        self.parser.use_bullpen = True
        team_key = 'FOO'
        pitchers = ['pitch{:02}'.format(idx) for idx in range(2 * self.parser.num_bullpen)]
        expected = pitchers[-self.parser.num_bullpen:]
        self.parser.update_bullpen(team_key, pitchers)
        self.assertIn(team_key, self.parser.bullpen)
        self.assertEqual(expected, list(self.parser.bullpen[team_key]))

    def test_get_bullpen_not_full(self):
        self.parser.use_bullpen = True
        team_key = 'FOO'
        pitchers = ['pitch00', 'pitch01', 'pitch02']
        expected = ['pitch00', 'pitch01', 'pitch02', None, None]
        self.parser.update_bullpen(team_key, pitchers)
        self.assertIn(team_key, self.parser.bullpen)
        self.assertEqual(expected, self.parser.get_bullpen(team_key))

    def test_get_bullpen_full(self):
        self.parser.use_bullpen = True
        team_key = 'FOO'
        pitchers = ['pitch{:02}'.format(idx) for idx in range(self.parser.num_bullpen)]
        self.parser.update_bullpen(team_key, pitchers)
        self.assertIn(team_key, self.parser.bullpen)
        self.assertEqual(pitchers, self.parser.get_bullpen(team_key))

    def test_append_visitor_batting(self):
        event = {
            'visteam': 'VIS',
            'hometeam': 'HOM',
            'visitor_or_home': '0',
            'batterID': 'bat00',
            'pitcherID': 'pitcher00',
            'field_C_playerID': 'catcher00',
            'field_1B_playerID': 'first00',
            'field_2B_playerID': 'second00',
            'field_3B_playerID': 'third00',
            'field_SS_playerID': 'short00',
            'field_LF_playerID': 'left00',
            'field_CF_playerID': 'center00',
            'field_RF_playerID': 'right00',
        }
        self.parser.append(event)

        self.assertEqual('VIS', self.parser.visitor.team_key)
        self.assertEqual('HOM', self.parser.home.team_key)

        self.assertIn('bat00', self.parser.visitor.batters)

        starting_fielders = {
            'pitcherID': 'pitcher00',
            'field_C_playerID': 'catcher00',
            'field_1B_playerID': 'first00',
            'field_2B_playerID': 'second00',
            'field_3B_playerID': 'third00',
            'field_SS_playerID': 'short00',
            'field_LF_playerID': 'left00',
            'field_CF_playerID': 'center00',
            'field_RF_playerID': 'right00',
        }
        self.assertEqual(starting_fielders, self.parser.home.fielders)

        self.assertIn('pitcher00', self.parser.home.pitchers)

        event = {
            'visteam': 'VIS',
            'hometeam': 'HOM',
            'visitor_or_home': '0',
            'batterID': 'bat01',
            'pitcherID': 'pitcher01',
            'field_C_playerID': 'catcher01',
            'field_1B_playerID': 'first01',
            'field_2B_playerID': 'second01',
            'field_3B_playerID': 'third01',
            'field_SS_playerID': 'short01',
            'field_LF_playerID': 'left01',
            'field_CF_playerID': 'center01',
            'field_RF_playerID': 'right01',
        }
        self.parser.append(event)

        self.assertIn('bat01', self.parser.visitor.batters)
        self.assertEqual(starting_fielders, self.parser.home.fielders)

        self.assertIn('pitcher01', self.parser.home.pitchers)

    def test_append_home_batting(self):
        event = {
            'visteam': 'VIS',
            'hometeam': 'HOM',
            'visitor_or_home': '1',
            'batterID': 'bat00',
            'pitcherID': 'pitcher00',
            'field_C_playerID': 'catcher00',
            'field_1B_playerID': 'first00',
            'field_2B_playerID': 'second00',
            'field_3B_playerID': 'third00',
            'field_SS_playerID': 'short00',
            'field_LF_playerID': 'left00',
            'field_CF_playerID': 'center00',
            'field_RF_playerID': 'right00',
        }
        self.parser.append(event)

        self.assertEqual('VIS', self.parser.visitor.team_key)
        self.assertEqual('HOM', self.parser.home.team_key)

        self.assertIn('bat00', self.parser.home.batters)

        starting_fielders = {
            'pitcherID': 'pitcher00',
            'field_C_playerID': 'catcher00',
            'field_1B_playerID': 'first00',
            'field_2B_playerID': 'second00',
            'field_3B_playerID': 'third00',
            'field_SS_playerID': 'short00',
            'field_LF_playerID': 'left00',
            'field_CF_playerID': 'center00',
            'field_RF_playerID': 'right00',
        }
        self.assertEqual(starting_fielders, self.parser.visitor.fielders)

        self.assertIn('pitcher00', self.parser.visitor.pitchers)

        event = {
            'visteam': 'VIS',
            'hometeam': 'HOM',
            'visitor_or_home': '1',
            'batterID': 'bat01',
            'pitcherID': 'pitcher01',
            'field_C_playerID': 'catcher01',
            'field_1B_playerID': 'first01',
            'field_2B_playerID': 'second01',
            'field_3B_playerID': 'third01',
            'field_SS_playerID': 'short01',
            'field_LF_playerID': 'left01',
            'field_CF_playerID': 'center01',
            'field_RF_playerID': 'right01',
        }
        self.parser.append(event)

        self.assertIn('bat01', self.parser.home.batters)
        self.assertEqual(starting_fielders, self.parser.visitor.fielders)

        self.assertIn('pitcher01', self.parser.visitor.pitchers)

    def test_fetch(self):
        self.parser.visitor.fielders = {
            'pitcherID': 'vis_pitcher',
            'field_C_playerID': 'vis_catcher',
            'field_1B_playerID': 'vis_first',
            'field_2B_playerID': 'vis_second',
            'field_3B_playerID': 'vis_third',
            'field_SS_playerID': 'vis_short',
            'field_LF_playerID': 'vis_left',
            'field_CF_playerID': 'vis_center',
            'field_RF_playerID': 'vis_right',
        }
        self.parser.home.fielders = {
            'pitcherID': 'home_pitcher',
            'field_C_playerID': 'home_catcher',
            'field_1B_playerID': 'home_first',
            'field_2B_playerID': 'home_second',
            'field_3B_playerID': 'home_third',
            'field_SS_playerID': 'home_short',
            'field_LF_playerID': 'home_left',
            'field_CF_playerID': 'home_center',
            'field_RF_playerID': 'home_right',
        }

        expected = {
            'vis_pitcher': 0,
            'vis_catcher': 1,
            'vis_first': 2,
            'vis_second': 3,
            'vis_third': 4,
            'vis_short': 5,
            'vis_left': 6,
            'vis_center': 7,
            'vis_right': 8,
            'home_pitcher': 9,
            'home_catcher': 10,
            'home_first': 11,
            'home_second': 12,
            'home_third': 13,
            'home_short': 14,
            'home_left': 15,
            'home_center': 16,
            'home_right': 17,
        }

        self.assertEqual(expected, self.parser.fetch())

    def test_fetch_use_dh(self):
        self.parser.visitor.use_dh = True
        self.parser.visitor.fielders = {
            'pitcherID': 'vis_pitcher',
            'field_C_playerID': 'vis_catcher',
            'field_1B_playerID': 'vis_first',
            'field_2B_playerID': 'vis_second',
            'field_3B_playerID': 'vis_third',
            'field_SS_playerID': 'vis_short',
            'field_LF_playerID': 'vis_left',
            'field_CF_playerID': 'vis_center',
            'field_RF_playerID': 'vis_right',
        }
        self.parser.visitor.designated_hitter = 'vis_dh'

        self.parser.home.use_dh = True
        self.parser.home.fielders = {
            'pitcherID': 'home_pitcher',
            'field_C_playerID': 'home_catcher',
            'field_1B_playerID': 'home_first',
            'field_2B_playerID': 'home_second',
            'field_3B_playerID': 'home_third',
            'field_SS_playerID': 'home_short',
            'field_LF_playerID': 'home_left',
            'field_CF_playerID': 'home_center',
            'field_RF_playerID': 'home_right',
        }
        self.parser.home.designated_hitter = 'home_dh'

        expected = {
            'vis_pitcher': 0,
            'vis_catcher': 1,
            'vis_first': 2,
            'vis_second': 3,
            'vis_third': 4,
            'vis_short': 5,
            'vis_left': 6,
            'vis_center': 7,
            'vis_right': 8,
            'vis_dh': 9,
            'home_pitcher': 10,
            'home_catcher': 11,
            'home_first': 12,
            'home_second': 13,
            'home_third': 14,
            'home_short': 15,
            'home_left': 16,
            'home_center': 17,
            'home_right': 18,
            'home_dh': 19,
        }

        self.assertEqual(expected, self.parser.fetch())

    def test_fetch_use_bullpen(self):
        self.parser.use_bullpen = True

        self.parser.visitor.team_key = 'VIS'
        self.parser.visitor.fielders = {
            'pitcherID': 'vis_pitcher',
            'field_C_playerID': 'vis_catcher',
            'field_1B_playerID': 'vis_first',
            'field_2B_playerID': 'vis_second',
            'field_3B_playerID': 'vis_third',
            'field_SS_playerID': 'vis_short',
            'field_LF_playerID': 'vis_left',
            'field_CF_playerID': 'vis_center',
            'field_RF_playerID': 'vis_right',
        }

        self.parser.home.team_key = 'HOM'
        self.parser.home.fielders = {
            'pitcherID': 'home_pitcher',
            'field_C_playerID': 'home_catcher',
            'field_1B_playerID': 'home_first',
            'field_2B_playerID': 'home_second',
            'field_3B_playerID': 'home_third',
            'field_SS_playerID': 'home_short',
            'field_LF_playerID': 'home_left',
            'field_CF_playerID': 'home_center',
            'field_RF_playerID': 'home_right',
        }

        vis_relief_pitchers = ['vis_rel00', 'vis_rel01', 'vis_rel02']
        self.parser.update_bullpen(self.parser.visitor.team_key, vis_relief_pitchers)

        home_relief_pitchers = ['home_rel00', 'home_rel01', 'home_rel02', 'home_rel03', 'home_rel04']
        self.parser.update_bullpen(self.parser.home.team_key, home_relief_pitchers)

        expected = {
            'vis_pitcher': 0,
            'vis_catcher': 1,
            'vis_first': 2,
            'vis_second': 3,
            'vis_third': 4,
            'vis_short': 5,
            'vis_left': 6,
            'vis_center': 7,
            'vis_right': 8,
            'vis_rel00': 9,
            'vis_rel01': 10,
            'vis_rel02': 11,
            # 'vis_rel03': 12,
            # 'vis_rel04': 13,
            'home_pitcher': 14,
            'home_catcher': 15,
            'home_first': 16,
            'home_second': 17,
            'home_third': 18,
            'home_short': 19,
            'home_left': 20,
            'home_center': 21,
            'home_right': 22,
            'home_rel00': 23,
            'home_rel01': 24,
            'home_rel02': 25,
            'home_rel03': 26,
            'home_rel04': 27,
        }

        self.assertEqual(expected, self.parser.fetch())

    def test_fetch_use_dh_use_bullpen(self):
        self.parser.use_bullpen = True

        self.parser.visitor.use_dh = True
        self.parser.visitor.team_key = 'VIS'
        self.parser.visitor.fielders = {
            'pitcherID': 'vis_pitcher',
            'field_C_playerID': 'vis_catcher',
            'field_1B_playerID': 'vis_first',
            'field_2B_playerID': 'vis_second',
            'field_3B_playerID': 'vis_third',
            'field_SS_playerID': 'vis_short',
            'field_LF_playerID': 'vis_left',
            'field_CF_playerID': 'vis_center',
            'field_RF_playerID': 'vis_right',
        }
        self.parser.visitor.designated_hitter = 'vis_dh'

        self.parser.home.use_dh = True
        self.parser.home.team_key = 'HOM'
        self.parser.home.fielders = {
            'pitcherID': 'home_pitcher',
            'field_C_playerID': 'home_catcher',
            'field_1B_playerID': 'home_first',
            'field_2B_playerID': 'home_second',
            'field_3B_playerID': 'home_third',
            'field_SS_playerID': 'home_short',
            'field_LF_playerID': 'home_left',
            'field_CF_playerID': 'home_center',
            'field_RF_playerID': 'home_right',
        }
        self.parser.home.designated_hitter = 'home_dh'

        vis_relief_pitchers = ['vis_rel00', 'vis_rel01', 'vis_rel02']
        self.parser.update_bullpen(self.parser.visitor.team_key, vis_relief_pitchers)

        home_relief_pitchers = ['home_rel00', 'home_rel01', 'home_rel02', 'home_rel03', 'home_rel04']
        self.parser.update_bullpen(self.parser.home.team_key, home_relief_pitchers)

        expected = {
            'vis_pitcher': 0,
            'vis_catcher': 1,
            'vis_first': 2,
            'vis_second': 3,
            'vis_third': 4,
            'vis_short': 5,
            'vis_left': 6,
            'vis_center': 7,
            'vis_right': 8,
            'vis_dh': 9,
            'vis_rel00': 10,
            'vis_rel01': 11,
            'vis_rel02': 12,
            # 'vis_rel03': 13,
            # 'vis_rel04': 14,
            'home_pitcher': 15,
            'home_catcher': 16,
            'home_first': 17,
            'home_second': 18,
            'home_third': 19,
            'home_short': 20,
            'home_left': 21,
            'home_center': 22,
            'home_right': 23,
            'home_dh': 24,
            'home_rel00': 25,
            'home_rel01': 26,
            'home_rel02': 27,
            'home_rel03': 28,
            'home_rel04': 29,
        }

        self.assertEqual(expected, self.parser.fetch())


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

        expected = 2 * self.pipeline.lineup_parser.num_batter
        self.assertEqual(expected, self.pipeline.num_player)

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

    def test_transform_angels_april_07_2022_use_dh(self):
        self.pipeline = Pipeline(use_dh=True)
        data = self.pipeline.extract(2022)
        gameID = 'ANA202204070'
        game = data[gameID]

        players, game_result, starting_lineup = self.pipeline.transform(game)

        expected = 2 * (self.pipeline.lineup_parser.num_batter + 1)
        self.assertEqual(expected, self.pipeline.num_player)

        # no dh for ohtas, so no key with value 19
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
            'branm003': 9,
            'ohtas001': 10,
            'stasm001': 11,
            'walsj001': 12,
            'duffm002': 13,
            'renda001': 14,
            'fletd002': 15,
            'adelj001': 16,
            'troum001': 17,
            'marsb002': 18,
        }
        self.assertDictEqual(expected, starting_lineup)

    def test_transform_angels_april_07_2022_use_bullpen(self):
        self.pipeline = Pipeline(use_bullpen=True)
        data = self.pipeline.extract(2022)
        gameID = 'ANA202204070'
        game = data[gameID]

        players, game_result, starting_lineup = self.pipeline.transform(game)

        expected = 2 * (self.pipeline.lineup_parser.num_batter + self.pipeline.lineup_parser.num_bullpen)
        self.assertEqual(expected, self.pipeline.num_player)

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
            'ohtas001': 14,
            'stasm001': 15,
            'walsj001': 16,
            'duffm002': 17,
            'renda001': 18,
            'fletd002': 19,
            'adelj001': 20,
            'troum001': 21,
            'marsb002': 22,
        }
        self.assertDictEqual(expected, starting_lineup)

        expected = ['loupa001', 'warra003', 'quijj001', 'teper001', 'brada001']
        self.assertListEqual(expected, list(self.pipeline.lineup_parser.bullpen['ANA']))

        expected = ['matop002', 'nerih001', 'presr001']
        self.assertListEqual(expected, list(self.pipeline.lineup_parser.bullpen['HOU']))

    def test_transform_angels_april_07_2022_use_dh_use_bullpen(self):
        self.pipeline = Pipeline(use_dh=True, use_bullpen=True)
        data = self.pipeline.extract(2022)
        gameID = 'ANA202204070'
        game = data[gameID]

        players, game_result, starting_lineup = self.pipeline.transform(game)

        expected = 2 * (self.pipeline.lineup_parser.num_batter + 1 + self.pipeline.lineup_parser.num_bullpen)
        self.assertEqual(expected, self.pipeline.num_player)

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
            'branm003': 9,
            'ohtas001': 15,
            'stasm001': 16,
            'walsj001': 17,
            'duffm002': 18,
            'renda001': 19,
            'fletd002': 20,
            'adelj001': 21,
            'troum001': 22,
            'marsb002': 23,
        }
        self.assertDictEqual(expected, starting_lineup)

        expected = ['loupa001', 'warra003', 'quijj001', 'teper001', 'brada001']
        self.assertListEqual(expected, list(self.pipeline.lineup_parser.bullpen['ANA']))

        expected = ['matop002', 'nerih001', 'presr001']
        self.assertListEqual(expected, list(self.pipeline.lineup_parser.bullpen['HOU']))

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
