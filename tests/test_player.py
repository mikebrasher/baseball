import unittest
import sqlite3
from baseball.player import Play, Batting, BaseRunning, Fielding, Player


class TestPlay(unittest.TestCase):

    def setUp(self):
        self.play = Play()

    def test_empty_play(self):
        self.play.parse('')
        self.assertEqual(1, self.play.unknown)

    def test_single_fielder(self):
        self.play.parse('8/F78')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['8'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.batter_out)

    def test_sacrifice_fly(self):
        self.play.parse('9/SF.3-H')
        self.assertEqual(1, self.play.sacrifice_fly)

    def test_sacrifice_hit(self):
        self.play.parse('23/SH.1-2')
        self.assertEqual(1, self.play.sacrifice_hit)

    def test_ground_ball(self):
        self.play.parse('3/G.2-3')
        self.assertEqual(1, self.play.ground_ball)

    def test_multiple_fielders(self):
        self.play.parse('63/G6M')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['3'], self.play.put_out)
        self.assertEqual(['6'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.batter_out)

        self.play.parse('143/G1')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['3'], self.play.put_out)
        self.assertEqual(['1', '4'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.batter_out)

        self.play.parse('54(B)/BG25/SH.1-2')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4'], self.play.put_out)
        self.assertEqual(['5'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.batter_out)

    def test_force_out(self):
        self.play.parse('54(1)/FO/G5.3-H;B-1')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4'], self.play.put_out)
        self.assertEqual(['5'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.force_out)

    def test_ground_double_play(self):
        self.play.parse('64(1)3/GDP/G6')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4', '3'], self.play.put_out)
        self.assertEqual(['6'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.ground_ball)
        self.assertEqual(1, self.play.double_play)
        self.assertEqual(1, self.play.ground_double_play)

        self.play.parse('4(1)3/G4/GDP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4', '3'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.ground_ball)
        self.assertEqual(1, self.play.double_play)
        self.assertEqual(1, self.play.ground_double_play)

    def test_ground_triple_play(self):
        self.play.parse('5(2)4(1)3/GTP')
        self.assertEqual(3, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5', '4', '3'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.ground_ball)
        self.assertEqual(1, self.play.triple_play)
        self.assertEqual(1, self.play.ground_triple_play)

    def test_line_double_play(self):
        self.play.parse('8(B)84(2)/LDP/L8')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['8', '4'], self.play.put_out)
        self.assertEqual(['8'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.line_drive)
        self.assertEqual(1, self.play.double_play)
        self.assertEqual(1, self.play.line_double_play)

        self.play.parse('3(B)3(1)/LDP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['3', '3'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.line_drive)
        self.assertEqual(1, self.play.double_play)
        self.assertEqual(1, self.play.line_double_play)

    def test_line_triple_play(self):
        self.play.parse('1(B)16(2)63(1)/LTP/L1')
        self.assertEqual(3, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['1', '6', '3'], self.play.put_out)
        self.assertEqual(['1', '6'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.line_drive)
        self.assertEqual(1, self.play.triple_play)
        self.assertEqual(1, self.play.line_triple_play)

    def test_unknown_play(self):
        self.play.parse('99/SH.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.unknown)

    def test_catcher_interference(self):
        self.play.parse('C/E2.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['2'], self.play.error)
        self.assertEqual(1, self.play.catcher_interference)

    def test_single(self):
        self.play.parse('S7')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.single)

    def test_double(self):
        self.play.parse('D7/G5')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.double)

    def test_triple(self):
        self.play.parse('T9/F9LD')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.triple)

    def test_ground_rule_double(self):
        self.play.parse('DGR/L9LS')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.double)
        self.assertEqual(1, self.play.ground_rule_double)

    def test_error_batter_on_base(self):
        self.play.parse('E1/TH/BG15.1-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['1'], self.play.error)
        self.assertEqual(1, self.play.error_batter_on_base)

        self.play.parse('E3.1-2;B-1')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['3'], self.play.error)
        self.assertEqual(1, self.play.error_batter_on_base)

        self.play.parse('3E1')  # error with assist
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual(['3'], self.play.assist)
        self.assertEqual(['1'], self.play.error)
        self.assertEqual(1, self.play.error_batter_on_base)

    def test_fielders_choice(self):
        self.play.parse('FC5/G5.3XH(52)',  '3X4(52)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual(['5'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.fielders_choice)

        self.play.parse('FC3/G3S.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.fielders_choice)

    def test_error_on_foul_fly_ball(self):
        self.play.parse('FLE5/P5F')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['5'], self.play.error)
        self.assertEqual(1, self.play.error_on_foul_fly_ball)

    def test_home_run(self):
        self.play.parse('H/L7D')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(1, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.home_run)
        self.assertEqual(1, self.play.run_batted_in)

        self.play.parse('HR/F78XD.2-H;1-H', '2-4;1-4')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(3, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.home_run)
        self.assertEqual(3, self.play.run_batted_in)

    def test_strike_out(self):
        self.play.parse('K')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(0, self.play.dropped_third_strike)

        self.play.parse('K23')  # dropped third strike
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['3'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(0, self.play.strike_out)
        self.assertEqual(1, self.play.dropped_third_strike)

    def test_strike_out_plus_stolen_base(self):
        self.play.parse('K+SB2')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['2'], self.play.stolen_base)

    def test_strike_out_plus_caught_stealing(self):
        self.play.parse('K+CS2(26)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertCountEqual(['2', '6'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['2'], self.play.caught_stealing)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_other_advance(self):
        self.play.parse('K+OA/DP.1X2(24)', '1X2(24)')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertCountEqual(['2', '4'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(1, self.play.other_advance)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_pick_off(self):
        self.play.parse('K+PO3(25)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertCountEqual(['2', '5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['3'], self.play.pick_off)
        self.assertEqual(1, self.play.double_play)

        self.play.parse('K+POCSH(251)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertCountEqual(['1', '2'], self.play.put_out)
        self.assertCountEqual(['2', '5'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['3'], self.play.pick_off)
        self.assertEqual(['H'], self.play.caught_stealing)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_passed_ball(self):
        self.play.parse('K+PB.1-2')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(1, self.play.passed_ball)

    def test_strike_out_plus_wild_pitch(self):
        self.play.parse('K+WP.B-1')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(1, self.play.wild_pitch)

        self.play.parse('K23+WP.2-3')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['3'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(0, self.play.strike_out)
        self.assertEqual(1, self.play.wild_pitch)

    def test_strike_out_plus_error(self):
        self.play.parse('K+E1.2-3')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['1'], self.play.error)
        self.assertEqual(1, self.play.strike_out)

    def test_no_play(self):
        self.play.parse('NP')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.no_play)

    def test_walk(self):
        self.play.parse('W')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_stolen_base(self):
        # The event can be SB%, CS%, PO%, PB, WP and E$.
        self.play.parse('W+SB3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.stolen_base)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_caught_stealing(self):
        self.play.parse('W+CS3(25)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.caught_stealing)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_pick_off(self):
        self.play.parse('W+PO3(25)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.pick_off)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_passed_ball(self):
        self.play.parse('W+PB.2-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.passed_ball)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_wild_pitch(self):
        self.play.parse('W+WP.2-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.wild_pitch)
        self.assertEqual(1, self.play.walk)

    def test_walk_plus_error(self):
        self.play.parse('W+E2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['2'], self.play.error)
        self.assertEqual(1, self.play.walk)

    def test_intentional_walk(self):
        self.play.parse('I')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.intentional_walk)

        self.play.parse('IW')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_stolen_base(self):
        self.play.parse('IW+SB3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.stolen_base)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_caught_stealing(self):
        self.play.parse('IW+CS3(25)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.caught_stealing)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_pick_off(self):
        self.play.parse('IW+PO3(25)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3'], self.play.pick_off)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_passed_ball(self):
        self.play.parse('IW+PB.2-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.passed_ball)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_wild_pitch(self):
        self.play.parse('IW+WP.2-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.wild_pitch)
        self.assertEqual(1, self.play.intentional_walk)

    def test_intentional_walk_plus_error(self):
        self.play.parse('IW+E2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['2'], self.play.error)
        self.assertEqual(1, self.play.intentional_walk)

    def test_balk(self):
        self.play.parse('BK.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.balk)

    def test_caught_stealing(self):
        # TODO: debug failing tests, starting here
        self.play.parse('CSH(12)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['2'], self.play.put_out)
        self.assertEqual(['1'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['H'], self.play.caught_stealing)

        self.play.parse('CS2(24).2-3')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['2'], self.play.caught_stealing)

        self.play.parse('CS2(2E4).1-3')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual(['4'], self.play.error)
        self.assertEqual(['2'], self.play.caught_stealing)

    def test_defensive_indifference(self):
        self.play.parse('DI.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.defensive_indifference)

    def test_other_advance(self):
        self.play.parse('OA.2X3(25)', '2X3(25)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.other_advance)

    def test_passed_ball(self):
        self.play.parse('PB.1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.passed_ball)

    def test_wild_pitch(self):
        self.play.parse('WP.2-3;1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.wild_pitch)

    def test_hit_by_pitch(self):
        self.play.parse('HP')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.hit_by_pitch)
        self.assertEqual(0, self.play.home_run)

    def test_pick_off(self):
        self.play.parse('PO2(14)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4'], self.play.put_out)
        self.assertEqual(['1'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['2'], self.play.pick_off)

        self.play.parse('PO1(E3).1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['3'], self.play.error)
        self.assertEqual(['1'], self.play.pick_off)

    def test_pick_off_caught_stealing(self):
        self.play.parse('POCS2(1361)')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['1'], self.play.put_out)
        self.assertEqual(['1', '3', '6'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['1'], self.play.pick_off)
        self.assertEqual(['2'], self.play.caught_stealing)

    def test_stolen_base(self):
        self.play.parse('SB2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['2'], self.play.stolen_base)

        self.play.parse('SB3;SB2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['3', '2'], self.play.stolen_base)

        self.play.parse('SBH;SB2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(['H', '2'], self.play.stolen_base)

    def test_error_on_advance(self):
        self.play.parse('FC6/G6', '1-2(E6);0-1')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['6'], self.play.error)
        self.assertEqual([], self.play.stolen_base)

    def test_putout_on_advance(self):
        self.play.parse('FC/G1', '3X4(125);1-3;0-2')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['1', '2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual([], self.play.stolen_base)

    def test_score_on_advance(self):
        self.play.parse('D7/G5', '3-4;2-4;1-4')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(3, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertCountEqual(['1', '2', '3'], self.play.score)
        self.assertEqual(3, self.play.run_batted_in)

        self.play.parse('HR/F9LD', '3-4;2-4;1-4')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(4, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertCountEqual(['B', '1', '2', '3'], self.play.score)
        self.assertEqual(4, self.play.run_batted_in)

        self.play.parse('HR/F89XD', '2-4;1-4;0-4')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(3, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertCountEqual(['B', '1', '2'], self.play.score)
        self.assertEqual(3, self.play.run_batted_in)

        self.play.parse('T7/L7LS', '2-4;1-4;0-4(E7/T4)')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(3, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['7'], self.play.error)
        self.assertCountEqual(['B', '1', '2'], self.play.score)
        self.assertEqual(2, self.play.run_batted_in)

    def test_runner_advance(self):
        self.play.parse('S9/G34', '3-4;2-3;1-2')
        self.assertCountEqual(['1-2', '2-3'], self.play.advance)

        self.play.parse('S8/G4+', '1-3')
        self.assertCountEqual(['1-3'], self.play.advance)

        self.play.parse('63/G6', '2-3')
        self.assertCountEqual(['2-3'], self.play.advance)

        self.play.parse('WP', '2-3')
        self.assertCountEqual(['2-3'], self.play.advance)

        self.play.parse('HP', '3-4;2-3;1-2')
        self.assertCountEqual(['1-2', '2-3'], self.play.advance)

        self.play.parse('W', '2-3;1-2')
        self.assertCountEqual(['1-2', '2-3'], self.play.advance)

    def test_run_batted_in_exclusion(self):
        self.play.parse('46(1)3/GDP/G4', '3-4')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(1, self.play.num_run)
        self.assertEqual(['6', '3'], self.play.put_out)
        self.assertEqual(['4'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(0, self.play.run_batted_in)

        self.play.parse('FC4/G4', '1-4(E4/T4);0-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(1, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['4'], self.play.error)
        self.assertEqual(0, self.play.run_batted_in)

        self.play.parse('E4/G4', '3-4;1-2;0-1')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(1, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual(['4'], self.play.error)
        self.assertEqual(0, self.play.run_batted_in)

        self.play.parse('WP', '3-4;1-2')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(1, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(0, self.play.run_batted_in)


class TestBatting(unittest.TestCase):

    def setUp(self):
        self.batting = Batting()

    def test_sacrifice(self):
        at_bats = (
            ('3/SH/BG5S', '2-3;1-2'),
            ('8/SF/F89D', '3-4'),
            ('13/SH/BG1S-', '1-2'),
            ('9/SF/L9D+', '3-4;2-3'),
            ('7/SF/DP/F7L', '3-4;1X2(724)'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.sacrifice_hit)
        self.assertEqual(3, self.batting.sacrifice_fly)
        self.assertEqual(0, self.batting.at_bat)

    def test_strike_out(self):
        at_bats = (
            ('K', ''),
            ('K', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.strike_out)

    def test_single(self):
        at_bats = (
            ('S68/G6', '3-4;1-2'),
            ('S7/G6+', '3-4;2-4;1-4'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.single)

    def test_double(self):
        at_bats = (
            ('D7/L7L+', ''),
            ('D9/G3', '1-3'),
            ('DGR/F9D', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(3, self.batting.double)

    def test_triple(self):
        at_bats = (
            ('T7/L7L+', ''),
            ('T39/G3+', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.triple)

    def test_home_run(self):
        at_bats = (
            ('HR/F7D', ''),
            ('HR/F78XD', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.home_run)

    def test_hit_by_pitch(self):
        at_bats = (
            ('HP', ''),
            ('HP', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.hit_by_pitch)

    def test_error_batter_on_base(self):
        at_bats = (
            ('E4/TH/G6D', '0-1'),
            ('E6/G6', '0-1'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.error_batter_on_base)

    def test_walk(self):
        at_bats = (
            ('W', ''),
            ('W', '1-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.walk)

    def test_intentional_walk(self):
        at_bats = (
            ('IW', ''),
            ('IW', '1-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.intentional_walk)

    def test_fielders_choice(self):
        at_bats = (
            ('FC/G5', '3X4(52);1-2;0-1'),
            ('FC/G6', '3X4(62);2-3;0-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(2, self.batting.fielders_choice)

    def test_run_batted_in(self):
        at_bats = (
            ('D7/G5', '3-4;2-4;1-4'),      # 3 RBI
            ('HR/F9LD', '3-4;2-4;1-4'),    # 4 RBI
            ('46(1)3/GDP/G4', '3-4'),      # excluded, ground double play
            ('FC4/G4', '1-4(E4/T4);0-2'),  # excluded, fielder's choice
            ('E4/G4', '3-4;1-2;0-1'),      # excluded, error on play
            ('WP', '3-4;1-2'),             # excluded, wild pitch
        )

        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(7, self.batting.run_batted_in)

    def test_hit(self):
        at_bats = (
            ('S68/G6', '3-4;1-2'),     # single
            ('D7/G5', '3-4;2-4;1-4'),  # double
            ('T7/L7L+', ''),           # triple
            ('HR/F7D', ''),            # home run
        )

        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(4, self.batting.hit)

    def test_at_bat(self):
        # sac hit/fly not counted as an at bat
        at_bats = (
            ('3/SH/BG5S', '2-3;1-2'),    # sac hit
            ('8/SF/F89D', '3-4'),        # sac fly
            ('K', ''),                   # strike out
            ('31/G34', ''),              # batter out
            ('D6/P8', ''),               # hit
            ('E6/G6M+', '2-3;0-1'),      # error, batter on base
            ('FC/G56', '2X3(546);0-2'),  # fielder's choice
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        self.assertEqual(1, self.batting.hit)
        self.assertEqual(5, self.batting.at_bat)
        self.assertAlmostEqual(0.2, self.batting.batting_average)

    def test_on_base_percentage(self):
        # sac hit/fly not counted as an at bat
        at_bats = (
            ('3/SH/BG5S', '2-3;1-2'),    # sac hit
            ('8/SF/F89D', '3-4'),        # sac fly
            ('K', ''),                   # strike out
            ('31/G34', ''),              # batter out
            ('D6/P8', ''),               # hit
            ('E6/G6M+', '2-3;0-1'),      # error, batter on base
            ('FC/G56', '2X3(546);0-2'),  # fielder's choice
            ('W', ''),                   # walk
            ('HP', ''),                  # hit by pitch
        )
        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        #  times reached base (H + BB + HBP)
        self.assertEqual(3, self.batting.times_reached_base)

        #  at bats plus walks plus hit by pitch plus sacrifice flies (AB + BB + HBP + SF)
        self.assertEqual(8, self.batting.at_bats_plus)

        # times reached base / at bats plus
        self.assertAlmostEqual(0.375, self.batting.on_base_percentage)

    def test_slugging(self):
        at_bats = (
            ('S68/G6', '3-4;1-2'),     # single   = 1 base
            ('D7/G5', '3-4;2-4;1-4'),  # double   = 2 bases
            ('T7/L7L+', ''),           # triple   = 3 bases
            ('HR/F7D', ''),            # home run = 4 bases
        )

        for the_play, base_running in at_bats:
            self.batting.parse(the_play, base_running)

        # sum of 10 bases
        self.assertEqual(10, self.batting.total_bases)

        # total bases / at bat
        self.assertAlmostEqual(2.5, self.batting.slugging)


class TestBaseRunning(unittest.TestCase):

    def setUp(self):
        self.base_running = BaseRunning()

    def test_caught_stealing(self):
        at_bats = (
            # the current runner was caught stealing
            ('CS2(24)', '', '1'),
            ('CS3(156)', '', '2'),
            ('CS3(25)', '', '2'),
            ('CSH(242)', '', '3'),
            # some other runner was caught stealing
            ('CS2(24)', '', '3'),
            ('CS3(156)', '', '1'),
            ('CS3(25)', '', '1'),
            ('CSH(242)', '', '2'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(4, self.base_running.caught_stealing)
        self.assertEqual(1, self.base_running.caught_stealing_second)
        self.assertEqual(2, self.base_running.caught_stealing_third)
        self.assertEqual(1, self.base_running.caught_stealing_home)

    def test_pick_off(self):
        at_bats = (
            # count these as pick off on runner
            ('PO1(13)', '', '1'),
            ('PO2(24)', '', '2'),
            ('PO3(25)', '', '3'),
            # error on pick off, still count against runner
            ('PO1(E2/TH)', '3-4;2-3;1-2', '1'),
            ('PO2(E1/TH)', '2-3', '2'),
            ('PO3(E1/TH)', '3-4', '3'),
            # successful pick off against some other runner
            ('PO1(13)', '', '2'),
            ('PO2(24)', '', '1'),
            ('PO3(25)', '', '1'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(6, self.base_running.pick_off)
        self.assertEqual(2, self.base_running.pick_off_first)
        self.assertEqual(2, self.base_running.pick_off_second)
        self.assertEqual(2, self.base_running.pick_off_third)

    def test_pick_off_caught_stealing(self):
        at_bats = (
            # pocs on runner
            ('POCS2(134)', '', '1'),
            ('POCS3(145)', '', '2'),
            # error on throw, still count against runner
            ('POCS2(13E4/TH)', '3-4', '1'),
            # pocs on some other runner
            ('POCS2(134)', '', '3'),
            ('POCS3(145)', '', '1'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(3, self.base_running.pick_off)
        self.assertEqual(2, self.base_running.pick_off_first)
        self.assertEqual(1, self.base_running.pick_off_second)
        self.assertEqual(0, self.base_running.pick_off_third)

        self.assertEqual(3, self.base_running.caught_stealing)
        self.assertEqual(2, self.base_running.caught_stealing_second)
        self.assertEqual(1, self.base_running.caught_stealing_third)
        self.assertEqual(0, self.base_running.caught_stealing_home)

    def test_score(self):
        at_bats = (
            ('S7/G6+', '3-4;2-4;1-4', '1'),
            ('S7/G6+', '3-4;2-4;1-4', '2'),
            ('S7/G6+', '3-4;2-4;1-4', '3'),
            ('D7/L7LS', '2-4;1X4(7525)', '1'),
            ('D7/L7LS', '2-4;1X4(7525)', '2'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(4, self.base_running.score_from_base)
        self.assertEqual(1, self.base_running.score_from_first)
        self.assertEqual(2, self.base_running.score_from_second)
        self.assertEqual(1, self.base_running.score_from_third)

    def test_stolen_base(self):
        at_bats = (
            # runner stole base
            ('SB2', '', '1'),
            ('SB3', '', '2'),
            ('SBH', '', '3'),
            ('SBH;SB2', '', '1'),
            ('SBH;SB2', '', '3'),
            # some other runner stole
            ('SB2', '', '3'),
            ('SB3', '', '1'),
            ('SBH', '', '1'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(5, self.base_running.stolen_base)
        self.assertEqual(2, self.base_running.steal_second)
        self.assertEqual(1, self.base_running.steal_third)
        self.assertEqual(2, self.base_running.steal_home)

    def test_advance_base(self):
        at_bats = (
            ('5(2)/FO/G5', '1-2;0-1', '1'),
            ('S9/G4', '1-2', '1'),
            ('E6/G6', '1-2', '1'),
            ('S8/G4+', '1-3', '1'),
            ('E4/G34', '1-3;0-1', '1'),
            ('53/G56S', '2-3', '2'),
            ('S4/G4', '2-3;1-2', '1'),
            ('S4/G4', '2-3;1-2', '2'),
            ('WP', '3-4;2-3;1-2', '1'),
            ('WP', '3-4;2-3;1-2', '2'),
        )
        for the_play, base_running, position in at_bats:
            self.base_running.parse(the_play, base_running, position)

        self.assertEqual(5, self.base_running.advance12)
        self.assertEqual(2, self.base_running.advance13)
        self.assertEqual(3, self.base_running.advance23)


class TestFielding(unittest.TestCase):

    def setUp(self):
        self.fielding = Fielding()

    def test_put_out(self):
        at_bats = (
            # the current fielder got a putout
            ('31/G3D+', '', '1'),
            ('62(3)/FO/G6S+', '2-3;1-2;0-1', '2'),
            ('63/G6', '', '3'),
            ('POCS2(134)', '', '4'),
            ('65(1)/FO/G6+', '0-1', '5'),
            ('56(2)/FO/BG25-', '1-2;0-1', '6'),
            ('7/F78D', '', '7'),
            ('8/L8D', '', '8'),
            ('9/F9', '', '9'),
            # some other fielder got a putout
            ('31/G3D+', '', '2'),
            ('62(3)/FO/G6S+', '2-3;1-2;0-1', '1'),
            ('63/G6', '', '1'),
            ('POCS2(134)', '', '1'),
            ('65(1)/FO/G6+', '0-1', '1'),
            ('56(2)/FO/BG25-', '1-2;0-1', '1'),
            ('7/F78D', '', '1'),
            ('8/L8D', '', '1'),
            ('9/F9', '', '1'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(9, self.fielding.put_out)

    def test_assist(self):
        at_bats = (
            # the current fielder got an assist
            ('31/G3D+', '', '3'),
            ('62(3)/FO/G6S+', '2-3;1-2;0-1', '6'),
            ('63/G6', '', '6'),
            ('POCS2(134)', '', '1'),
            ('65(1)/FO/G6+', '0-1', '6'),
            ('56(2)/FO/BG25-', '1-2;0-1', '5'),
            # some other fielder got an assist
            ('31/G3D+', '', '2'),
            ('62(3)/FO/G6S+', '2-3;1-2;0-1', '1'),
            ('63/G6', '', '1'),
            ('POCS2(134)', '', '2'),
            ('65(1)/FO/G6+', '0-1', '1'),
            ('56(2)/FO/BG25-', '1-2;0-1', '1'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(6, self.fielding.assist)

    def test_error(self):
        at_bats = (
            # the current fielder got an error
            ('S1/BG2', '1-4;0-2(E1/T4)', '1'),
            ('SB2', '1-3(E2/T4)', '2'),
            ('E3/G34', '2-3;1-2;0-1', '3'),
            ('FC4/G4M+', '2-3;1-2(E4);0-1', '4'),
            ('S5/G5', '1-3(E5/T4);0-2', '5'),
            ('E6/TH/G6M', '0-2', '6'),
            ('E7/F7LD', '0-2', '7'),
            ('E8/F89D', '0-2', '8'),
            ('S9/G34', '2-4;1-3;0-2(E9/T4)', '9'),
            # some other fielder got an error
            ('S1/BG2', '1-4;0-2(E1/T4)', '4'),
            ('SB2', '1-3(E2/T4)', '4'),
            ('E3/G34', '2-3;1-2;0-1', '1'),
            ('FC4/G4M+', '2-3;1-2(E4);0-1', '1'),
            ('S5/G5', '1-3(E5/T4);0-2', '4'),
            ('E6/TH/G6M', '0-2', '3'),
            ('E7/F7LD', '0-2', '4'),
            ('E8/F89D', '0-2', '5'),
            ('S9/G34', '2-4;1-3;0-2(E9/T4)', '6'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(9, self.fielding.error)

    def test_double_play(self):
        at_bats = (
            # the current fielder was part of a double play
            ('5/L56/DP', '1X1(53)', '5'),
            ('5/L56/DP', '1X1(53)', '3'),
            ('36(1)3/GDP/G3', '', '3'),
            ('36(1)3/GDP/G3', '', '6'),
            ('6(1)3/GDP/G6M', '3-4', '3'),
            ('6(1)3/GDP/G6M', '3-4', '6'),
            ('7/SF/DP/F78D+', '3-4;2X3(7545)', '4'),
            ('7/SF/DP/F78D+', '3-4;2X3(7545)', '5'),
            ('7/SF/DP/F78D+', '3-4;2X3(7545)', '7'),
            # some other fielder was part of a double play
            ('5/L56/DP', '1X1(53)', '6'),
            ('36(1)3/GDP/G3', '', '2'),
            ('6(1)3/GDP/G6M', '3-4', '4'),
            ('7/SF/DP/F78D+', '3-4;2X3(7545)', '8'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(9, self.fielding.double_play)

    def test_triple_play(self):
        at_bats = (
            # the current fielder was part of a triple play
            ('6/L6/TP', '2X2(64);1X1(43)', '3'),
            ('6/L6/TP', '2X2(64);1X1(43)', '4'),
            ('6/L6/TP', '2X2(64);1X1(43)', '6'),
            ('8/F89XD+/TP,', '2X2(5);1X1(85)', '5'),
            ('8/F89XD+/TP,', '2X2(5);1X1(85)', '8'),
            ('5(2)4(1)3/GTP', '', '3'),
            ('5(2)4(1)3/GTP', '', '4'),
            ('5(2)4(1)3/GTP', '', '5'),
            # some other fielder was part of a triple play
            ('6/L6/TP', '2X2(64);1X1(43)', '5'),
            ('8/F89XD+/TP,', '2X2(5);1X1(85)', '7'),
            ('5(2)4(1)3/GTP', '', '6'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(8, self.fielding.triple_play)

    def test_passed_ball(self):
        at_bats = (
            # the catcher on a passed ball
            ('PB', '2-3', '2'),
            ('K+PB', '0-1', '2'),
            ('W+PB', '3-4;2-3', '2'),
            # some other fielder was part of a triple play
            ('PB', '2-3', '1'),
            ('K+PB', '0-1', '3'),
            ('W+PB', '3-4;2-3', '4'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(3, self.fielding.passed_ball)

    def test_num_out(self):
        at_bats = (
            # top of first inning for CHA202207240
            ('3/G3,', '', '3'),
            ('9/F9D', '', '5'),
            ('S8/G6M', '', '8'),
            ('S7/G56+', '1-2', '4'),
            ('8/L89D', '', '3'),
            # top of second inning for CHA202207240
            ('S7/L7L', '', '7'),
            ('53/G5S', '1-2', '9'),
            ('K', '', '1'),
            ('WP', '2-3', '6'),
            ('K', '', '7'),
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        # all fielders get an out played regardless of their involvement in the out
        self.assertEqual(6, self.fielding.num_out)
        self.assertAlmostEqual(2.0, self.fielding.inning_at_position)

    def test_fielding(self):
        at_bats = (
            ('65(1)/FO/G6+', '0-1', '5'),        # 3B putout
            ('56(2)/FO/BG25-', '1-2;0-1', '5'),  # 3B assist
            ('S5/G5', '1-3(E5/T4);0-2', '5'),    # 3B error
        )
        for the_play, base_running, position in at_bats:
            self.fielding.parse(the_play, base_running, position)

        self.assertEqual(1, self.fielding.put_out)
        self.assertEqual(1, self.fielding.assist)
        self.assertEqual(1, self.fielding.error)
        self.assertEqual(3, self.fielding.total_chance)
        self.assertAlmostEqual(2/3, self.fielding.fielding)


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.con = sqlite3.connect("../seasons.db")
        self.cur = self.con.cursor()
        self.delta = 5e-3

    # baseball almanac doesn't seem to record hit by pitch, so some numbers are off
    # https://www.baseball-almanac.com/players/hittinglogs.php?p=bettsmo01&y=2022
    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #     April 2022 Totals 74 	19 	17 	2 	0 	3 	6 	13 	0 	16 	0 	0 	0 	.230 	.345 	.378
    #       May 2022 Totals	114 31 	39 	10 	0 	12 	27 	13 	0 	19 	0 	0 	1 	.342 	.406 	.746
    #      June 2022 Totals	57 	3 	11 	1 	0 	2 	7 	1 	0 	12 	0 	0 	0 	.193 	.207 	.316
    #      July 2022 Totals	101 18 	26 	5 	1 	6 	12 	10 	0 	17 	0 	0 	1 	.257 	.321 	.505
    #    August 2022 Totals	109 30 	36 	11 	1 	9 	18 	8 	0 	20 	0 	0 	1 	.330 	.373 	.697
    # September 2022 Totals	104 14 	24 	10 	1 	3 	12 	9 	0 	17 	0 	0 	1 	.231 	.289 	.433
    #   October 2022 Totals	13 	2 	2 	1 	0 	0 	0 	1 	0 	3 	0 	0 	0 	.154 	.214 	.231
    #    2022 Yearly Totals 572 117 155 40 	3 	35 	82 	55 	0 	104 0 	0 	4 	.271 	.333 	.535

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #     April 2022 Totals 74 	19 	17 	2 	0 	3 	6 	13 	0 	16 	0 	0 	0 	.230 	.345 	.378
    def test_offense_mookie_april_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='04')

        p.parse_batting()
        self.assertEqual(74, p.batting.at_bat)
        self.assertEqual(17, p.batting.hit)
        self.assertEqual(2, p.batting.double)
        self.assertEqual(0, p.batting.triple)
        self.assertEqual(3, p.batting.home_run)
        self.assertEqual(6, p.batting.run_batted_in)
        self.assertEqual(13, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(16, p.batting.strike_out)
        self.assertEqual(1, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(0, p.batting.sacrifice_fly)
        self.assertEqual(31, p.batting.times_reached_base)
        self.assertEqual(88, p.batting.at_bats_plus)
        self.assertEqual(28, p.batting.total_bases)
        self.assertAlmostEqual(0.230, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.352, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.378, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(11, p.base_running.advance12)
        self.assertEqual(3, p.base_running.advance13)
        self.assertEqual(9, p.base_running.advance23)
        self.assertEqual(0, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(0, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(16, p.base_running.score_from_base)
        self.assertEqual(2, p.base_running.score_from_first)
        self.assertEqual(6, p.base_running.score_from_second)
        self.assertEqual(8, p.base_running.score_from_third)
        self.assertEqual(3, p.base_running.stolen_base)
        self.assertEqual(3, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(19, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #       May 2022 Totals	114 31 	39 	10 	0 	12 	27 	13 	0 	19 	0 	0 	1 	.342 	.406 	.746
    def test_offense_mookie_may_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='05')

        p.parse_batting()
        self.assertEqual(114, p.batting.at_bat)
        self.assertEqual(39, p.batting.hit)
        self.assertEqual(10, p.batting.double)
        self.assertEqual(0, p.batting.triple)
        self.assertEqual(12, p.batting.home_run)
        self.assertEqual(27, p.batting.run_batted_in)
        self.assertEqual(13, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(19, p.batting.strike_out)
        self.assertEqual(1, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(1, p.batting.sacrifice_fly)
        self.assertEqual(53, p.batting.times_reached_base)
        self.assertEqual(129, p.batting.at_bats_plus)
        self.assertEqual(85, p.batting.total_bases)
        self.assertAlmostEqual(0.342, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.411, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.746, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(12, p.base_running.advance12)
        self.assertEqual(5, p.base_running.advance13)
        self.assertEqual(7, p.base_running.advance23)
        self.assertEqual(1, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(1, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(1, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(1, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(19, p.base_running.score_from_base)
        self.assertEqual(4, p.base_running.score_from_first)
        self.assertEqual(6, p.base_running.score_from_second)
        self.assertEqual(9, p.base_running.score_from_third)
        self.assertEqual(1, p.base_running.stolen_base)
        self.assertEqual(1, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(31, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #      June 2022 Totals	57 	3 	11 	1 	0 	2 	7 	1 	0 	12 	0 	0 	0 	.193 	.207 	.316
    def test_offense_mookie_june_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='06')

        p.parse_batting()
        self.assertEqual(57, p.batting.at_bat)
        self.assertEqual(11, p.batting.hit)
        self.assertEqual(1, p.batting.double)
        self.assertEqual(0, p.batting.triple)
        self.assertEqual(2, p.batting.home_run)
        self.assertEqual(7, p.batting.run_batted_in)
        self.assertEqual(1, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(12, p.batting.strike_out)
        self.assertEqual(0, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(0, p.batting.sacrifice_fly)
        self.assertEqual(12, p.batting.times_reached_base)
        self.assertEqual(58, p.batting.at_bats_plus)
        self.assertEqual(18, p.batting.total_bases)
        self.assertAlmostEqual(0.193, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.207, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.316, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(3, p.base_running.advance12)
        self.assertEqual(1, p.base_running.advance13)
        self.assertEqual(1, p.base_running.advance23)
        self.assertEqual(0, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(0, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(1, p.base_running.score_from_base)
        self.assertEqual(0, p.base_running.score_from_first)
        self.assertEqual(0, p.base_running.score_from_second)
        self.assertEqual(1, p.base_running.score_from_third)
        self.assertEqual(2, p.base_running.stolen_base)
        self.assertEqual(2, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(3, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #      July 2022 Totals	101 18 	26 	5 	1 	6 	12 	10 	0 	17 	0 	0 	1 	.257 	.321 	.505
    def test_offense_mookie_july_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='07')

        p.parse_batting()
        self.assertEqual(101, p.batting.at_bat)
        # 1 fielder's choice, so only 25 hits
        self.assertEqual(25, p.batting.hit)
        self.assertEqual(5, p.batting.double)
        self.assertEqual(1, p.batting.triple)
        self.assertEqual(6, p.batting.home_run)
        self.assertEqual(12, p.batting.run_batted_in)
        self.assertEqual(10, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(17, p.batting.strike_out)
        self.assertEqual(2, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(1, p.batting.sacrifice_fly)
        self.assertEqual(37, p.batting.times_reached_base)
        self.assertEqual(114, p.batting.at_bats_plus)
        self.assertEqual(50, p.batting.total_bases)
        self.assertAlmostEqual(0.248, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.325, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.495, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(9, p.base_running.advance12)
        self.assertEqual(2, p.base_running.advance13)
        self.assertEqual(4, p.base_running.advance23)
        self.assertEqual(0, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(0, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(12, p.base_running.score_from_base)
        self.assertEqual(2, p.base_running.score_from_first)
        self.assertEqual(6, p.base_running.score_from_second)
        self.assertEqual(4, p.base_running.score_from_third)
        self.assertEqual(1, p.base_running.stolen_base)
        self.assertEqual(1, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(18, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #    August 2022 Totals	109 30 	36 	11 	1 	9 	18 	8 	0 	20 	0 	0 	1 	.330 	.373 	.697
    def test_offense_mookie_august_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='08')

        p.parse_batting()
        self.assertEqual(109, p.batting.at_bat)
        self.assertEqual(36, p.batting.hit)
        self.assertEqual(11, p.batting.double)
        self.assertEqual(1, p.batting.triple)
        self.assertEqual(9, p.batting.home_run)
        self.assertEqual(18, p.batting.run_batted_in)
        self.assertEqual(8, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(20, p.batting.strike_out)
        self.assertEqual(2, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(1, p.batting.sacrifice_fly)
        self.assertEqual(46, p.batting.times_reached_base)
        self.assertEqual(120, p.batting.at_bats_plus)
        self.assertEqual(76, p.batting.total_bases)
        self.assertAlmostEqual(0.330, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.383, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.697, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(10, p.base_running.advance12)
        self.assertEqual(4, p.base_running.advance13)
        self.assertEqual(10, p.base_running.advance23)
        self.assertEqual(0, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(1, p.base_running.pick_off)
        self.assertEqual(1, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(21, p.base_running.score_from_base)
        self.assertEqual(0, p.base_running.score_from_first)
        self.assertEqual(9, p.base_running.score_from_second)
        self.assertEqual(12, p.base_running.score_from_third)
        self.assertEqual(5, p.base_running.stolen_base)
        self.assertEqual(5, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(30, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    # September 2022 Totals	104 14 	24 	10 	1 	3 	12 	9 	0 	17 	0 	0 	1 	.231 	.289 	.433
    def test_offense_mookie_september_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='09')

        p.parse_batting()
        self.assertEqual(104, p.batting.at_bat)
        self.assertEqual(24, p.batting.hit)
        self.assertEqual(10, p.batting.double)
        self.assertEqual(1, p.batting.triple)
        self.assertEqual(3, p.batting.home_run)
        self.assertEqual(12, p.batting.run_batted_in)
        self.assertEqual(9, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(17, p.batting.strike_out)
        self.assertEqual(2, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(1, p.batting.sacrifice_fly)
        self.assertEqual(35, p.batting.times_reached_base)
        self.assertEqual(116, p.batting.at_bats_plus)
        self.assertEqual(45, p.batting.total_bases)
        self.assertAlmostEqual(0.231, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.302, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.433, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(5, p.base_running.advance12)
        self.assertEqual(3, p.base_running.advance13)
        self.assertEqual(10, p.base_running.advance23)
        self.assertEqual(1, p.base_running.caught_stealing)
        self.assertEqual(1, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(0, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(11, p.base_running.score_from_base)
        self.assertEqual(1, p.base_running.score_from_first)
        self.assertEqual(1, p.base_running.score_from_second)
        self.assertEqual(9, p.base_running.score_from_third)
        self.assertEqual(0, p.base_running.stolen_base)
        self.assertEqual(0, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(14, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #   October 2022 Totals	13 	2 	2 	1 	0 	0 	0 	1 	0 	3 	0 	0 	0 	.154 	.214 	.231
    def test_offense_mookie_october_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='10')

        p.parse_batting()
        self.assertEqual(13, p.batting.at_bat)
        # don't test runs, since it includes base running
        self.assertEqual(2, p.batting.hit)
        self.assertEqual(1, p.batting.double)
        self.assertEqual(0, p.batting.triple)
        self.assertEqual(0, p.batting.home_run)
        self.assertEqual(0, p.batting.run_batted_in)
        self.assertEqual(1, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(3, p.batting.strike_out)
        self.assertEqual(0, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(0, p.batting.sacrifice_fly)
        self.assertEqual(3, p.batting.times_reached_base)
        self.assertEqual(14, p.batting.at_bats_plus)
        self.assertEqual(3, p.batting.total_bases)
        self.assertAlmostEqual(0.154, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.214, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.231, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(0, p.base_running.advance12)
        self.assertEqual(0, p.base_running.advance13)
        self.assertEqual(0, p.base_running.advance23)
        self.assertEqual(0, p.base_running.caught_stealing)
        self.assertEqual(0, p.base_running.caught_stealing_second)
        self.assertEqual(0, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(0, p.base_running.pick_off)
        self.assertEqual(0, p.base_running.pick_off_first)
        self.assertEqual(0, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(2, p.base_running.score_from_base)
        self.assertEqual(1, p.base_running.score_from_first)
        self.assertEqual(1, p.base_running.score_from_second)
        self.assertEqual(0, p.base_running.score_from_third)
        self.assertEqual(0, p.base_running.stolen_base)
        self.assertEqual(0, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(2, p.batting.home_run + p.base_running.score_from_base)

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #    2022 Yearly Totals 572 117 155 40 	3 	35 	82 	55 	0 	104 0 	0 	4 	.271 	.333 	.535
    def test_offense_mookie_total_2022(self):
        p = Player('bettm001', self.cur, year='2022')

        p.parse_batting()
        self.assertEqual(572, p.batting.at_bat)
        # 1 fielder's choice, so only 154 hits
        self.assertEqual(154, p.batting.hit)
        self.assertEqual(40, p.batting.double)
        self.assertEqual(3, p.batting.triple)
        self.assertEqual(35, p.batting.home_run)
        self.assertEqual(82, p.batting.run_batted_in)
        self.assertEqual(55, p.batting.walk)
        self.assertEqual(0, p.batting.intentional_walk)
        self.assertEqual(104, p.batting.strike_out)
        self.assertEqual(8, p.batting.hit_by_pitch)
        self.assertEqual(0, p.batting.sacrifice_hit)
        self.assertEqual(4, p.batting.sacrifice_fly)
        self.assertEqual(217, p.batting.times_reached_base)
        self.assertEqual(639, p.batting.at_bats_plus)
        self.assertEqual(305, p.batting.total_bases)
        self.assertAlmostEqual(0.269, p.batting.batting_average, delta=self.delta)
        self.assertAlmostEqual(0.340, p.batting.on_base_percentage, delta=self.delta)
        self.assertAlmostEqual(0.533, p.batting.slugging, delta=self.delta)

        p.parse_base_running()
        self.assertEqual(50, p.base_running.advance12)
        self.assertEqual(18, p.base_running.advance13)
        self.assertEqual(41, p.base_running.advance23)
        self.assertEqual(2, p.base_running.caught_stealing)
        self.assertEqual(1, p.base_running.caught_stealing_second)
        self.assertEqual(1, p.base_running.caught_stealing_third)
        self.assertEqual(0, p.base_running.caught_stealing_home)
        self.assertEqual(2, p.base_running.pick_off)
        self.assertEqual(1, p.base_running.pick_off_first)
        self.assertEqual(1, p.base_running.pick_off_second)
        self.assertEqual(0, p.base_running.pick_off_third)
        self.assertEqual(82, p.base_running.score_from_base)
        self.assertEqual(10, p.base_running.score_from_first)
        self.assertEqual(29, p.base_running.score_from_second)
        self.assertEqual(43, p.base_running.score_from_third)
        self.assertEqual(12, p.base_running.stolen_base)
        self.assertEqual(12, p.base_running.steal_second)
        self.assertEqual(0, p.base_running.steal_third)
        self.assertEqual(0, p.base_running.steal_home)

        self.assertEqual(117, p.batting.home_run + p.base_running.score_from_base)

    # starting lineup for game 4/8/22 vs Rockies
    # pitcher = Player('buehw001', self.cur, year='2022')       # Walker Buehler
    def test_fielding_dodgers_pitcher_2022(self):
        # https://www.baseball-reference.com/players/b/buehlwa01.shtml
        # Pos   Inn 	Ch 	    PO 	    A 	E 	DP 	Fld
        # P	    65.0	11	    5	    6	0	0	1.000
        p = Player('buehw001', self.cur, year='2022')       # Walker Buehler
        p.parse_fielding()
        self.assertEqual(196, p.fielding.num_out)
        self.assertEqual(11, p.fielding.total_chance)
        self.assertEqual(5, p.fielding.put_out)
        self.assertEqual(6, p.fielding.assist)
        self.assertEqual(0, p.fielding.error)
        self.assertEqual(0, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(65.3333, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(1.0, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_catcher_2022(self):
        # https://www.baseball-reference.com/players/s/smithwi05.shtml
        # Pos   Inn 	Ch 	    PO 	    A 	E 	DP 	Fld     PB
        # C	    956.1	1003	968	    32	3	6	.997	4
        p = Player('smitw003', self.cur, year='2022')  # Will Smith
        p.parse_fielding()
        self.assertEqual(2886, p.fielding.num_out)
        self.assertEqual(1019, p.fielding.total_chance)
        self.assertEqual(985, p.fielding.put_out)
        self.assertEqual(31, p.fielding.assist)
        self.assertEqual(3, p.fielding.error)
        self.assertEqual(6, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(4, p.fielding.passed_ball)
        self.assertAlmostEqual(962.0, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.997, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_first_base_2022(self):
        # https://www.baseball-reference.com/players/f/freemfr01.shtml
        # Pos   Inn 	Ch 	    PO 	    A 	E 	DP 	Fld
        # 1B	1377.2	1251	1155	91	5	100	.996
        p = Player('freef001', self.cur, year='2022')  # Freddie Freeman
        p.parse_fielding()
        self.assertEqual(4152, p.fielding.num_out)
        self.assertEqual(1250, p.fielding.total_chance)
        self.assertEqual(1155, p.fielding.put_out)
        self.assertEqual(90, p.fielding.assist)
        self.assertEqual(5, p.fielding.error)
        self.assertEqual(100, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(1384.0, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.996, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_second_base_2022(self):
        # https://www.baseball-reference.com/players/l/luxga01.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld
        # 2B	819.2	337	148	180	9	45	.973
        # OF	205.1	29	29	0	0	0	1.000
        # SS	31.0	14	3	11	0	3	1.000
        # sum   1056.0  380 180 191 9   48  .979
        p = Player('lux-g001', self.cur, year='2022')  # Gavin Lux
        p.parse_fielding()
        self.assertEqual(3187, p.fielding.num_out)
        self.assertEqual(348, p.fielding.total_chance)
        self.assertEqual(180, p.fielding.put_out)
        self.assertEqual(159, p.fielding.assist)
        self.assertEqual(9, p.fielding.error)
        self.assertEqual(48, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(1062.3333, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.974, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_third_base_2022(self):
        # https://www.baseball-reference.com/players/m/muncyma01.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld
        # 3B	713.0	222	51	161	10	25	.955
        # 2B	223.1	106	35	69	2	13	.981
        # sum   936.1   328 86  230 12  38  .963
        p = Player('muncm001', self.cur, year='2022')  # Max Muncy
        p.parse_fielding()
        self.assertEqual(2837, p.fielding.num_out)
        self.assertEqual(317, p.fielding.total_chance)
        self.assertEqual(90, p.fielding.put_out)
        self.assertEqual(215, p.fielding.assist)
        self.assertEqual(12, p.fielding.error)
        self.assertEqual(39, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(945.6667, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.962, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_short_stop_2022(self):
        # https://www.baseball-reference.com/players/t/turnetr01.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld
        # SS	1386.2	524	174	334	16	54	.969
        p = Player('turnt001', self.cur, year='2022')  # Trea Turner
        p.parse_fielding()
        self.assertEqual(4179, p.fielding.num_out)
        self.assertEqual(500, p.fielding.total_chance)
        self.assertEqual(174, p.fielding.put_out)
        self.assertEqual(310, p.fielding.assist)
        self.assertEqual(16, p.fielding.error)
        self.assertEqual(54, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(1393.0, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.968, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_left_field_2022(self):
        # https://www.baseball-reference.com/players/t/tayloch03.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld
        # OF	777.0	170	165	3	2	2	.988
        # 2B	170.0	80	27	53	0	8	1.000
        # sum   947.0   250 192 56  2   10  .992
        p = Player('taylc001', self.cur, year='2022')  # Chris Taylor
        p.parse_fielding()
        self.assertEqual(2869, p.fielding.num_out)
        self.assertEqual(243, p.fielding.total_chance)
        self.assertEqual(192, p.fielding.put_out)
        self.assertEqual(49, p.fielding.assist)
        self.assertEqual(2, p.fielding.error)
        self.assertEqual(10, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(956.3333, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.992, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_center_field_2022(self):
        # https://www.baseball-reference.com/players/b/bellico01.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld
        # CF    1223.0 327	322	2	3	0	.991
        p = Player('bellc002', self.cur, year='2022')  # Cody Bellinger
        p.parse_fielding()
        self.assertEqual(3689, p.fielding.num_out)
        self.assertEqual(327, p.fielding.total_chance)
        self.assertEqual(322, p.fielding.put_out)
        self.assertEqual(2, p.fielding.assist)
        self.assertEqual(3, p.fielding.error)
        self.assertEqual(0, p.fielding.double_play)
        self.assertEqual(0, p.fielding.triple_play)
        self.assertEqual(0, p.fielding.passed_ball)
        self.assertAlmostEqual(1229.6667, p.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.991, p.fielding.fielding, delta=self.delta)

    def test_fielding_dodgers_right_field_2022(self):
        # https://www.baseball-reference.com/players/b/bettsmo01.shtml
        # Pos   Inn 	Ch 	PO 	A 	E 	DP 	Fld%
        # RF    1154.1	308	298	8	2	4	.994
        # 2B    46.0	24	9	15	0	7	1.000
        # sum   1200.1  332 307 23  2   11  .994
        right_field = Player('bettm001', self.cur, year='2022')  # Mookie Betts
        right_field.parse_fielding()
        self.assertEqual(3618, right_field.fielding.num_out)
        self.assertEqual(327, right_field.fielding.total_chance)
        self.assertEqual(307, right_field.fielding.put_out)
        self.assertEqual(18, right_field.fielding.assist)
        self.assertEqual(2, right_field.fielding.error)
        self.assertEqual(11, right_field.fielding.double_play)
        self.assertEqual(0, right_field.fielding.triple_play)
        self.assertEqual(0, right_field.fielding.passed_ball)
        self.assertAlmostEqual(1206.0, right_field.fielding.inning_at_position, delta=self.delta)
        self.assertAlmostEqual(0.994, right_field.fielding.fielding, delta=self.delta)


if __name__ == '__main__':
    unittest.main()
