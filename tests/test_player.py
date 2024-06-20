import unittest
import sqlite3
from baseball.player import Play, Batting, Player


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
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.sacrifice_hit)
        self.assertEqual(3, self.batting.sacrifice_fly)
        self.assertEqual(0, self.batting.at_bat)

    def test_strike_out(self):
        at_bats = (
            ('K', ''),
            ('K', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.strike_out)

    def test_single(self):
        at_bats = (
            ('S68/G6', '3-4;1-2'),
            ('S7/G6+', '3-4;2-4;1-4'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.single)

    def test_double(self):
        at_bats = (
            ('D7/L7L+', ''),
            ('D9/G3', '1-3'),
            ('DGR/F9D', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(3, self.batting.double)

    def test_triple(self):
        at_bats = (
            ('T7/L7L+', ''),
            ('T39/G3+', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.triple)

    def test_home_run(self):
        at_bats = (
            ('HR/F7D', ''),
            ('HR/F78XD', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.home_run)

    def test_hit_by_pitch(self):
        at_bats = (
            ('HP', ''),
            ('HP', ''),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.hit_by_pitch)

    def test_error_batter_on_base(self):
        at_bats = (
            ('E4/TH/G6D', '0-1'),
            ('E6/G6', '0-1'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.error_batter_on_base)

    def test_walk(self):
        at_bats = (
            ('W', ''),
            ('W', '1-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.walk)

    def test_intentional_walk(self):
        at_bats = (
            ('IW', ''),
            ('IW', '1-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(2, self.batting.intentional_walk)

    def test_fielders_choice(self):
        at_bats = (
            ('FC/G5', '3X4(52);1-2;0-1'),
            ('FC/G6', '3X4(62);2-3;0-2'),
        )
        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

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
            self.batting.parse_at_bat(the_play, base_running)

        self.assertEqual(7, self.batting.run_batted_in)

    def test_hit(self):
        at_bats = (
            ('S68/G6', '3-4;1-2'),     # single
            ('D7/G5', '3-4;2-4;1-4'),  # double
            ('T7/L7L+', ''),           # triple
            ('HR/F7D', ''),            # home run
        )

        for the_play, base_running in at_bats:
            self.batting.parse_at_bat(the_play, base_running)

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
            self.batting.parse_at_bat(the_play, base_running)

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
            self.batting.parse_at_bat(the_play, base_running)

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
            self.batting.parse_at_bat(the_play, base_running)

        # sum of 10 bases
        self.assertEqual(10, self.batting.total_bases)

        # total bases / at bat
        self.assertAlmostEqual(2.5, self.batting.slugging)


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
    def test_batting_mookie_april_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='04')
        p.parse_batting()

        self.assertEqual(74, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #       May 2022 Totals	114 31 	39 	10 	0 	12 	27 	13 	0 	19 	0 	0 	1 	.342 	.406 	.746
    def test_batting_mookie_may_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='05')
        p.parse_batting()

        self.assertEqual(114, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #      June 2022 Totals	57 	3 	11 	1 	0 	2 	7 	1 	0 	12 	0 	0 	0 	.193 	.207 	.316
    def test_batting_mookie_june_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='06')
        p.parse_batting()

        self.assertEqual(57, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #      July 2022 Totals	101 18 	26 	5 	1 	6 	12 	10 	0 	17 	0 	0 	1 	.257 	.321 	.505
    def test_batting_mookie_july_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='07')
        p.parse_batting()

        self.assertEqual(101, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #    August 2022 Totals	109 30 	36 	11 	1 	9 	18 	8 	0 	20 	0 	0 	1 	.330 	.373 	.697
    def test_batting_mookie_august_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='08')
        p.parse_batting()

        self.assertEqual(109, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    # September 2022 Totals	104 14 	24 	10 	1 	3 	12 	9 	0 	17 	0 	0 	1 	.231 	.289 	.433
    def test_batting_mookie_september_2022(self):
        p = Player('bettm001', self.cur, year='2022', month='09')
        p.parse_batting()

        self.assertEqual(104, p.batting.at_bat)
        # don't test runs, since it includes base running
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #   October 2022 Totals	13 	2 	2 	1 	0 	0 	0 	1 	0 	3 	0 	0 	0 	.154 	.214 	.231
    def test_batting_mookie_october_2022(self):
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

    #                       AB	R	H	2B	3B	HR	RBI	BB	IBB	K	HBP	SH	SF	AVG     OBP	    SLG
    #    2022 Yearly Totals 572 117 155 40 	3 	35 	82 	55 	0 	104 0 	0 	4 	.271 	.333 	.535
    def test_batting_mookie_total_2022(self):
        p = Player('bettm001', self.cur, year='2022')
        p.parse_batting()

        self.assertEqual(572, p.batting.at_bat)
        # don't test runs, since it includes base running
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


if __name__ == '__main__':
    unittest.main()