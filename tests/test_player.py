import unittest
import sqlite3
from baseball.player import Player, Play


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.con = sqlite3.connect('../seasons.db')
        self.cur = self.con.cursor()
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
        self.assertEqual([], self.play.put_out)
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
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['2'], self.play.stolen_base)

    def test_strike_out_plus_caught_stealing(self):
        self.play.parse('K+CS2(26)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['6'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['2'], self.play.caught_stealing)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_other_advance(self):
        self.play.parse('K+OA/DP.1X2(24)', '1X2(24)')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['4'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(1, self.play.other_advance)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_pick_off(self):
        self.play.parse('K+PO3(25)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['5'], self.play.put_out)
        self.assertEqual(['2'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['3'], self.play.pick_off)
        self.assertEqual(1, self.play.double_play)

        self.play.parse('K+POCSH(251)/DP')
        self.assertEqual(2, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual(['1'], self.play.put_out)
        self.assertEqual(['2', '5'], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(['H'], self.play.pick_off)
        self.assertEqual(['H'], self.play.caught_stealing)
        self.assertEqual(1, self.play.double_play)

    def test_strike_out_plus_passed_ball(self):
        self.play.parse('K+PB.1-2')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(1, self.play.strike_out)
        self.assertEqual(1, self.play.passed_ball)

    def test_strike_out_plus_wild_pitch(self):
        self.play.parse('K+WP.B-1')
        self.assertEqual(1, self.play.num_out)
        self.assertEqual(0, self.play.num_run)
        self.assertEqual([], self.play.put_out)
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
        self.assertEqual([], self.play.put_out)
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
        self.assertEqual(['2'], self.play.pick_off)
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
        self.assertEqual(3, self.play.run_batted_in)

        self.play.parse('HR/F9LD', '3-4;2-4;1-4')
        self.assertEqual(0, self.play.num_out)
        self.assertEqual(4, self.play.num_run)
        self.assertEqual([], self.play.put_out)
        self.assertEqual([], self.play.assist)
        self.assertEqual([], self.play.error)
        self.assertEqual(4, self.play.run_batted_in)

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

    def test_batting(self):
        # p = Player('bettm001', self.cur)
        # p.parse_batting()
        # p.batting.print_stats()
        # TODO: implement this stub
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
