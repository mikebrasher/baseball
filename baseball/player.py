import re


class Play:
    def __init__(self):
        # direct play codes
        self.balk = 0
        self.batter_out = 0
        self.catcher_interference = 0
        self.caught_stealing = 0
        self.defensive_indifference = 0
        self.double = 0
        self.dropped_third_strike = 0
        self.error_batter_on_base = 0
        self.error_on_foul_fly_ball = 0
        self.fielders_choice = 0
        self.ground_rule_double = 0
        self.home_run = 0
        self.hit_by_pitch = 0
        self.intentional_walk = 0
        self.no_play = 0
        self.other_advance = 0
        self.passed_ball = 0
        self.single = 0
        self.strike_out = 0
        self.triple = 0
        self.unknown = 0
        self.walk = 0
        self.wild_pitch = 0

        # modifier codes
        self.bunt_grounder = 0
        self.bunt_pop_up = 0
        self.double_play = 0
        self.fly_ball = 0
        self.force_out = 0
        self.ground_ball = 0
        self.ground_double_play = 0
        self.ground_triple_play = 0
        self.line_double_play = 0
        self.line_drive = 0
        self.line_triple_play = 0
        self.pop_up = 0
        self.sacrifice_fly = 0
        self.sacrifice_hit = 0
        self.triple_play = 0

        # derived statistics
        self.put_out = []
        self.assist = []
        self.error = []
        self.score = []
        self.stolen_base = []
        self.pick_off = []
        self.caught_stealing = []
        self.advance = []
        self.num_out = 0
        self.num_run = 0
        self.run_batted_in = 0

        # other members
        self.separator = '|'

    def reset(self):
        # direct play codes
        self.balk = 0
        self.batter_out = 0
        self.catcher_interference = 0
        self.caught_stealing = 0
        self.defensive_indifference = 0
        self.double = 0
        self.dropped_third_strike = 0
        self.error_batter_on_base = 0
        self.error_on_foul_fly_ball = 0
        self.fielders_choice = 0
        self.ground_rule_double = 0
        self.ground_double_play = 0
        self.home_run = 0
        self.hit_by_pitch = 0
        self.intentional_walk = 0
        self.no_play = 0
        self.other_advance = 0
        self.passed_ball = 0
        self.sacrifice_fly = 0
        self.sacrifice_hit = 0
        self.single = 0
        self.strike_out = 0
        self.triple = 0
        self.unknown = 0
        self.walk = 0
        self.wild_pitch = 0

        # modifier codes
        self.bunt_grounder = 0
        self.bunt_pop_up = 0
        self.double_play = 0
        self.fly_ball = 0
        self.force_out = 0
        self.ground_ball = 0
        self.ground_double_play = 0
        self.ground_triple_play = 0
        self.line_double_play = 0
        self.line_drive = 0
        self.line_triple_play = 0
        self.pop_up = 0
        self.sacrifice_fly = 0
        self.sacrifice_hit = 0
        self.triple_play = 0

        # derived statistics
        self.put_out = []
        self.assist = []
        self.error = []
        self.score = []
        self.stolen_base = []
        self.pick_off = []
        self.caught_stealing = []
        self.advance = []
        self.num_out = 0
        self.num_run = 0
        self.run_batted_in = 0

    # assume pick off or caught stealing is present
    def parse_pick_off_caught_stealing(self, play, fielders):
        combo_idx = play.find('POCS')
        pick_off_idx = play.find('PO')
        caught_stealing_idx = play.find('CS')
        if combo_idx >= 0:
            stolen_base = play[combo_idx + 4]
            # count POCS2 as pick off on first and stolen base for second, etc.
            if stolen_base == '2':
                runner = '1'
            elif stolen_base == '3':
                runner = '2'
            elif stolen_base == 'H':
                runner = '3'
            else:
                runner = 'B'
            self.pick_off.append(runner)
            self.caught_stealing.append(stolen_base)
        elif pick_off_idx >= 0:
            self.pick_off.append(play[pick_off_idx + 2])
        elif caught_stealing_idx >= 0:
            self.caught_stealing.append(play[caught_stealing_idx + 2])

        for f in fielders:
            error_idx = f.find('E')
            if error_idx >= 0:
                self.error.append(f[error_idx + 1])
                self.assist += list(f[:error_idx])
            else:
                self.put_out.append(f[-1])
                self.assist += list(f[:-1])

    def parse_extra_event(self, play, fielders):
        # the extra event can be one of SB%, CS%, OA, PO%, PB, WP and E$.
        if play.find('PO') >= 0 or play.find('CS') >= 0:
            self.parse_pick_off_caught_stealing(play, fielders)
        elif play.find('SB') >= 0:
            stolen_base_idx = play.find('SB')
            self.stolen_base.append(play[stolen_base_idx + 2])
        elif play.find('OA') >= 0:
            self.other_advance = 1
        elif play.find('PB') >= 0:
            self.passed_ball = 1
        elif play.find('WP') >= 0:
            self.wild_pitch = 1
        elif play.find('E') >= 0:
            error_idx = play.find('E')
            self.error.append(play[error_idx + 1])
        else:
            self.unknown = 1

    def parse_main_play(self, main_play):
        # outs coded as integer position codes, last one gets a put out, every other gets an assist
        # i.e. 63 for shortstop to first base, or 64(1)43 for double play
        targets = re.findall(r'\((.*?)\)', main_play)
        main_play = re.sub(r'\([B1234]*?\)', self.separator, main_play)
        events = main_play.strip(self.separator).split(self.separator)
        first = events[0]
        if len(first) > 0 and first[0].isdigit():
            self.batter_out = 1
            if first == '99':
                # code for unknown play
                # don't award putout or assists
                self.unknown = 1
            else:
                for fielders in events:
                    error_idx = fielders.find('E')
                    if error_idx >= 0:
                        self.error.append(fielders[error_idx + 1])
                        self.assist += list(fielders[:error_idx])
                        self.error_batter_on_base = 1
                    else:
                        self.put_out.append(fielders[-1])
                        self.assist += list(fielders[:-1])
        elif first.find('WP') == 0:  # parse longer codes first, must be before W
            self.wild_pitch = 1
        elif first.find('HP') == 0:  # must occur before H
            self.hit_by_pitch = 1
        elif first.find('HR') == 0 or first.find('H') == 0:
            self.home_run = 1
            self.score.append('B')
        elif first.find('IW') == 0 or first.find('I') == 0:
            self.intentional_walk = 1
        elif first.find('NP') == 0:
            self.no_play = 1  # for substitutions
        elif first.find('BK') == 0:
            self.balk = 1
        elif first.find('DGR') == 0:  # must occur before D
            self.double = 1
            self.ground_rule_double = 1
        elif first.find('DI') == 0:  # must occur before D
            self.defensive_indifference += 1  # no attempt to prevent stolen base
        elif first.find('PO') == 0 or first.find('CS') == 0:  # must occur before C
            self.parse_pick_off_caught_stealing(first, targets)
        elif first.find('PB') == 0:
            self.passed_ball = 1
        elif first.find('E') == 0:
            self.error.append(first[1])
            self.error_batter_on_base = 1
        elif first.find('SB') == 0:  # must be before S
            for advance in first.split(';'):
                stolen_base_idx = advance.find('SB')
                self.stolen_base.append(advance[stolen_base_idx + 2])
        elif first.find('K') == 0:
            sub_event = first.split('+')[0]
            if sub_event == 'K':
                self.strike_out = 1
            else:
                self.dropped_third_strike = 1
                self.put_out.append(sub_event[-1])
                self.assist += list(sub_event[1:-1])
        elif first.find('S') == 0:
            self.single = 1
        elif first.find('D') == 0:
            self.double = 1
        elif first.find('T') == 0:
            self.triple = 1
        elif first.find('W') == 0:
            self.walk = 1
        elif first.find('FC') == 0:
            self.fielders_choice = 1
        elif first.find('FLE') == 0:
            self.error_on_foul_fly_ball = 1
            self.error.append(first[3])
        elif first.find('C') == 0:
            self.catcher_interference = 1
        elif first.find('OA') == 0:
            self.other_advance = 1
        else:
            self.unknown = 1

        # parse any additional events present
        if first.find('+') >= 0:
            self.parse_extra_event(first, targets)

    def parse_modifier(self, modifier):
        if modifier.find('FO') == 0:
            self.force_out = 1
        elif modifier.find('GDP') == 0:
            self.ground_ball = 1
            self.double_play = 1
            self.ground_double_play = 1
        elif modifier.find('LDP') == 0:
            self.line_drive = 1
            self.double_play = 1
            self.line_double_play = 1
        elif modifier.find('GTP') == 0:
            self.ground_ball = 1
            self.triple_play = 1
            self.ground_triple_play = 1
        elif modifier.find('LTP') == 0:
            self.line_drive = 1
            self.triple_play = 1
            self.line_triple_play = 1
        elif modifier.find('SF') == 0:
            self.sacrifice_fly = 1
        elif modifier.find('SH') == 0:
            self.sacrifice_hit = 1
        elif modifier.find('DP') == 0:
            self.double_play = 1
        elif modifier.find('TP') == 0:
            self.triple_play = 1
        elif modifier.find('E') == 0:
            # appears as part of a C/E2 for catcher interference
            self.error.append(modifier[1])
        elif modifier.find('G') == 0:
            self.ground_ball = 1
        elif modifier.find('L') == 0:
            self.line_drive = 1
        elif modifier.find('P') == 0:
            self.pop_up = 1
        elif modifier.find('F') == 0:
            self.fly_ball = 1
        elif modifier.find('BG') == 0:
            self.bunt_grounder = 1
        elif modifier.find('BP') == 0:
            self.bunt_pop_up = 1

    def parse_base_running(self, base_running):
        for advance in base_running.split(';'):
            # errors on base running, e.g. 1-2(E6), list position which incurred error
            error_idx = advance.find('E')
            if error_idx >= 0:
                self.error.append(advance[error_idx + 1])

            if advance.find('X') >= 0:
                # outs on base running, e.g. 3X4(52), list positions assigned assist and putout
                self.num_out += 1
                fielders = re.findall(r'\((.*?)\)', advance)
                for f in fielders:
                    self.put_out.append(f[-1])
                    self.assist += list(f[:-1])

            # score runs regardless of errors
            # batter scores
            if (advance.find('0-4') >= 0) or advance.find('0-H') >= 0:
                # add if not present, i.e. triple, score on error
                if 'B' not in self.score:
                    self.score.append('B')

            # score from first
            if (advance.find('1-4') >= 0) or advance.find('1-H') >= 0:
                self.score.append('1')

            # score from second
            if (advance.find('2-4') >= 0) or advance.find('2-H') >= 0:
                self.score.append('2')

            # score from third
            if (advance.find('3-4') >= 0) or advance.find('3-H') >= 0:
                self.score.append('3')

            # runner's advance a base
            # first to second
            if advance.find('1-2') >= 0:
                self.advance.append('1-2')

            # first to third
            if advance.find('1-3') >= 0:
                self.advance.append('1-3')

            # second to third
            if advance.find('2-3') >= 0:
                self.advance.append('2-3')

            # count all scores for runs
            self.num_run = len(self.score)

            # for run batted in
            # don't include ground into double play
            # don't include errors
            # don't include wild pitches
            # runs after error on fly ball are not officially counted, but ignoring this rule
            if self.ground_double_play == 0 and len(self.error) == 0 and self.wild_pitch == 0:
                self.run_batted_in = self.num_run

            # runs after an error on fly ball that would have been the third out
            # are not officially counted as earned runs for RBI,
            # but ignoring this rule for simplicity as it depends on previous events

    def parse(self, play, base_running=''):
        self.reset()

        # play is split into codes
        # main_play/modifier/hit_description
        codes = play.split('/')
        self.parse_main_play(codes[0])
        for modifier in codes[1:]:
            self.parse_modifier(modifier)

        self.parse_base_running(base_running)

        # include all putouts from fielding play and base running
        self.num_out = len(self.put_out) + self.strike_out


class Batting:
    def __init__(self):
        self.play = Play()

        # accumulate statistics
        self.sacrifice_hit = 0
        self.sacrifice_fly = 0
        self.out = 0
        self.strike_out = 0
        self.single = 0
        self.double = 0
        self.triple = 0
        self.home_run = 0
        self.hit_by_pitch = 0
        self.error_batter_on_base = 0
        self.walk = 0
        self.intentional_walk = 0
        self.fielders_choice = 0
        self.run = 0
        self.run_batted_in = 0

        # derived stats
        self.hit = 0
        self.at_bat = 0
        self.batting_average = 0.0
        self.times_reached_base = 0
        self.at_bats_plus = 0
        self.on_base_percentage = 0.0
        self.total_bases = 0
        self.slugging = 0.0

    def reset(self):
        # accumulate statistics
        self.sacrifice_hit = 0
        self.sacrifice_fly = 0
        self.out = 0
        self.strike_out = 0
        self.single = 0
        self.double = 0
        self.triple = 0
        self.home_run = 0
        self.hit_by_pitch = 0
        self.error_batter_on_base = 0
        self.walk = 0
        self.intentional_walk = 0
        self.fielders_choice = 0
        self.run = 0
        self.run_batted_in = 0

        # derived stats
        self.hit = 0
        self.at_bat = 0
        self.batting_average = 0.0
        self.times_reached_base = 0
        self.at_bats_plus = 0
        self.on_base_percentage = 0.0
        self.total_bases = 0
        self.slugging = 0.0

    def parse(self, the_play, base_running):
        self.play.parse(the_play, base_running)

        self.sacrifice_hit += self.play.sacrifice_hit
        self.sacrifice_fly += self.play.sacrifice_fly
        if self.play.sacrifice_hit == 0 and self.play.sacrifice_fly == 0:
            # don't count sacs as out for at bat
            self.out += self.play.batter_out

        self.strike_out += self.play.strike_out
        self.single += self.play.single
        self.double += self.play.double
        self.triple += self.play.triple
        self.home_run += self.play.home_run
        self.hit_by_pitch += self.play.hit_by_pitch
        self.error_batter_on_base += self.play.error_batter_on_base
        self.walk += self.play.walk
        self.intentional_walk += self.play.intentional_walk
        self.fielders_choice += self.play.fielders_choice
        self.run += self.play.num_run
        self.run_batted_in += self.play.run_batted_in

        self.hit = self.single + self.double + self.triple + self.home_run
        self.at_bat = self.strike_out + self.out + self.hit + self.error_batter_on_base + self.fielders_choice

        # hits divided by at bats (H/AB)
        if self.at_bat > 0:
            self.batting_average = self.hit / self.at_bat

        #  times reached base (H + BB + HBP) divided by
        self.times_reached_base = self.hit + self.walk + self.hit_by_pitch
        #  at bats plus walks plus hit by pitch plus sacrifice flies (AB + BB + HBP + SF)
        self.at_bats_plus = self.at_bat + self.walk + self.hit_by_pitch + self.sacrifice_fly
        if self.at_bats_plus > 0:
            self.on_base_percentage = self.times_reached_base / self.at_bats_plus

        # total bases achieved on hits divided by at-bats (TB/AB)
        self.total_bases = self.single + 2 * self.double + 3 * self.triple + 4 * self.home_run
        if self.at_bat > 0:
            self.slugging = self.total_bases / self.at_bat

    def print_stats(self):
        header = ['AB', 'R', 'H', '2B', '3B', 'HR', 'RBI',
                  'BB', 'IBB', 'K', 'HBP', 'SH', 'SF',
                  'AVG', 'OBP', 'SLG']
        data = [
            self.at_bat,
            self.run,
            self.hit,
            self.double,
            self.triple,
            self.home_run,
            self.run_batted_in,
            self.walk,
            self.intentional_walk,
            self.strike_out,
            self.hit_by_pitch,
            self.sacrifice_hit,
            self.sacrifice_fly,
            self.batting_average,
            self.on_base_percentage,
            self.slugging,
        ]
        str_data = ['{:5d}'.format(d) if type(d) is int else '{:5.3f}'.format(d) for d in data]
        print('\t'.join(header))
        print('\t'.join(str_data))


class BaseRunning:
    def __init__(self):
        self.play = Play()

        self.caught_stealing = 0
        self.caught_stealing_second = 0
        self.caught_stealing_third = 0
        self.caught_stealing_home = 0
        self.pick_off = 0
        self.pick_off_first = 0
        self.pick_off_second = 0
        self.pick_off_third = 0
        self.score_from_base = 0
        self.score_from_first = 0
        self.score_from_second = 0
        self.score_from_third = 0
        self.stolen_base = 0
        self.steal_second = 0
        self.steal_third = 0
        self.steal_home = 0
        self.advance12 = 0
        self.advance13 = 0
        self.advance23 = 0

    def reset(self):
        self.caught_stealing = 0
        self.caught_stealing_second = 0
        self.caught_stealing_third = 0
        self.caught_stealing_home = 0
        self.pick_off = 0
        self.pick_off_first = 0
        self.pick_off_second = 0
        self.pick_off_third = 0
        self.score_from_base = 0
        self.score_from_first = 0
        self.score_from_second = 0
        self.score_from_third = 0
        self.stolen_base = 0
        self.steal_second = 0
        self.steal_third = 0
        self.steal_home = 0
        self.advance12 = 0
        self.advance13 = 0
        self.advance23 = 0

    def parse(self, the_play, base_running, position):
        self.play.parse(the_play, base_running)

        for base in self.play.caught_stealing:
            if base == '2' and position == '1':
                self.caught_stealing_second += 1
            elif base == '3' and position == '2':
                self.caught_stealing_third += 1
            elif (base == 'H' or base == '4') and position == '3':
                self.caught_stealing_home += 1
        self.caught_stealing = self.caught_stealing_second + self.caught_stealing_third + self.caught_stealing_home

        for base in self.play.pick_off:
            if base == position == '1':
                self.pick_off_first += 1
            elif base == position == '2':
                self.pick_off_second += 1
            elif base == position == '3':
                self.pick_off_third += 1
        self.pick_off = self.pick_off_first + self.pick_off_second + self.pick_off_third

        for base in self.play.score:
            if base == position == '1':
                self.score_from_first += 1
            elif base == position == '2':
                self.score_from_second += 1
            elif base == position == '3':
                self.score_from_third += 1
        self.score_from_base = self.score_from_first + self.score_from_second + self.score_from_third

        for base in self.play.stolen_base:
            if base == '2' and position == '1':
                self.steal_second += 1
            elif base == '3' and position == '2':
                self.steal_third += 1
            elif (base == 'H' or base == '4') and position == '3':
                self.steal_home += 1
        self.stolen_base = self.steal_second + self.steal_third + self.steal_home

        for bases in self.play.advance:
            if bases == '1-2' and position == '1':
                self.advance12 += 1
            elif bases == '1-3' and position == '1':
                self.advance13 += 1
            elif bases == '2-3' and position == '2':
                self.advance23 += 1


class Pitching:
    def __init__(self):
        # pitching even enum
        self.sacrifice_hit = 0
        self.sacrifice_fly = 0
        self.out = 0
        self.error = 0
        self.stolen_base = 0
        self.single = 0
        self.double = 0
        self.triple = 0
        self.home_run = 0
        self.walk = 0
        self.strike_out = 0
        self.intentional_walk = 0
        self.fielders_choice = 0
        self.no_play = 0
        self.hit_by_pitch = 0
        self.passed_ball = 0
        self.error_on_foul_fly_ball = 0
        self.defensive_indifference = 0
        self.wild_pitch = 0
        self.balk = 0
        self.pick_off = 0
        self.caught_stealing = 0
        self.unknown = 0

        # derived stats
        self.earned_run = 0
        self.earned_run_average = 0.0
        self.innings_pitched = 0.0
        self.hit = 0
        self.run = 0

    def parse_match_up(self, play, base_running, inning, vis_score, home_score, outs):
        events = play.split('/')
        first = events[0]
        is_out, put_out, _ = parse_play(first)
        curr_out = self.out
        curr_strike_out = self.strike_out
        if is_out:
            self.out += len(put_out)
        elif first.find('E') == 0:
            self.error += 1
        elif first.find('SB') == 0:
            self.stolen_base += 1
        elif first == 'WP':
            self.wild_pitch += 1
        elif first == 'DI':
            self.defensive_indifference += 1  # no attempt to prevent stolen base
        elif first.find('S') == 0:
            self.single += 1
        elif first.find('D') == 0:
            self.double += 1
        elif first.find('T') == 0:
            self.triple += 1
        elif first == 'H' or first == 'HR':
            self.home_run += 1
            self.run += 1
            self.earned_run += 1
        elif first.find('W') == 0:
            self.walk += 1
        elif first.find('K') == 0:
            self.strike_out += 1
        elif first == 'I' or first == 'IW':
            self.intentional_walk += 1
        elif first.find('FC') == 0:
            self.fielders_choice += 1
        elif first == 'NP':
            self.no_play += 1  # for substitutions
        elif first == 'HP':
            self.hit_by_pitch += 1
        elif first == 'PB':
            self.passed_ball += 1
        elif first.find('FLE') == 0:
            self.error_on_foul_fly_ball += 1
        elif first == 'BK':
            self.balk += 1
        elif first.find('PO') == 0:
            self.pick_off += 1
        elif first.find('CS') == 0:
            self.caught_stealing += 1
        else:
            self.unknown += 1

        if base_running.find('1-4') >= 0:
            self.run += 1

        if base_running.find('2-4') >= 0:
            self.run += 1

        if base_running.find('3-4') >= 0:
            self.run += 1

        # don't include errors on fielding the hit
        if first.find('E') < 0:
            # or on the play at home, i.e. '1-4(E6)'
            earned_run_list = ['1-4', '2-4', '3-4']
            for advance in base_running.split(';'):
                if advance in earned_run_list:
                    self.earned_run += 1
                if advance.find('X') >= 0:
                    self.out += 1

        self.innings_pitched = (self.out + self.strike_out + self.pick_off + self.caught_stealing) / 3.0
        if self.innings_pitched > 0:
            self.earned_run_average = self.earned_run * 9.0 / self.innings_pitched

        self.hit = self.single + self.double + self.triple + self.home_run

    def print_stats(self):
        header = ['ERA', 'IP', 'K', 'H', 'ER', 'R', 'HR', 'BB', 'IBB', 'WP', 'HBP', 'BK']
        str_header = ['{:5s}'.format(h) for h in header]
        print('\t'.join(str_header))

        data = [
            self.earned_run_average,
            self.innings_pitched,
            self.strike_out,
            self.hit,
            self.earned_run,
            self.run,
            self.home_run,
            self.walk,
            self.intentional_walk,
            self.wild_pitch,
            self.hit_by_pitch,
            self.balk,
        ]
        str_data = ['{:<5d}'.format(d) if type(d) is int else '{:5.3f}'.format(d) for d in data]
        print('\t'.join(str_data))


class Fielding:
    def __init__(self):
        self.play = Play()

        # accumulate statistics
        self.sacrifice_hit = 0
        self.sacrifice_fly = 0
        self.out_played = 0
        self.put_out = 0
        self.assist = 0
        self.error = 0
        self.error = 0
        self.stolen_base = 0
        self.single = 0
        self.double = 0
        self.triple = 0
        self.home_run = 0
        self.walk = 0
        self.strike_out = 0
        self.intentional_walk = 0
        self.fielders_choice = 0
        self.no_play = 0
        self.hit_by_pitch = 0
        self.passed_ball = 0
        self.error_on_foul_fly_ball = 0
        self.defensive_indifference = 0
        self.wild_pitch = 0
        self.balk = 0
        self.pick_off = 0
        self.caught_stealing = 0
        self.unknown = 0

        # derived stats
        self.inning_at_position = 0
        self.total_chance = 0
        self.double_play = 0
        self.triple_play = 0
        self.fielding = 0.0

    def parse_play(self, play, base_running, position, inning, vis_score, home_score, outs):
        events = play.split('/')
        first = events[0]
        is_out, put_out, assist = parse_play(first)
        curr_out = self.out_played
        curr_strike_out = self.strike_out
        if is_out:
            count_out = len(put_out)
            self.out_played += count_out
            self.put_out += sum([1 for po in put_out if po == position])
            self.assist += sum([1 for a in assist if a == position])
            if position in put_out or position in assist:
                if count_out == 2:
                    self.double_play += 1
                elif count_out == 3:
                    self.triple_play += 1
        elif first.find('E') == 0:
            if first[1] == position:
                self.error += 1
        elif first.find('SB') == 0:
            self.stolen_base += 1
        elif first == 'WP':
            self.wild_pitch += 1
        elif first == 'DI':
            self.defensive_indifference += 1  # no attempt to prevent stolen base
        elif first.find('S') == 0:
            self.single += 1
        elif first.find('D') == 0:
            self.double += 1
        elif first.find('T') == 0:
            self.triple += 1
        elif first == 'H' or first == 'HR':
            self.home_run += 1
        elif first.find('W') == 0:
            self.walk += 1
        elif first.find('K') == 0:
            self.strike_out += 1
        elif first == 'I' or first == 'IW':
            self.intentional_walk += 1
        elif first.find('FC') == 0:
            self.fielders_choice += 1
        elif first == 'NP':
            self.no_play += 1  # for substitutions
        elif first == 'HP':
            self.hit_by_pitch += 1
        elif first == 'PB':
            self.passed_ball += 1
        elif first.find('FLE') == 0:
            self.error_on_foul_fly_ball += 1
        elif first == 'BK':
            self.balk += 1
        elif first.find('PO') == 0:
            self.pick_off += 1
        elif first.find('CS') == 0:
            self.caught_stealing += 1
        else:
            self.unknown += 1

        for advance in base_running.split(';'):
            error_idx = advance.find('E')
            if error_idx >= 0:
                if advance[error_idx + 1] == position:
                    self.error += 1
            if advance.find('X') >= 0:
                self.out_played += 1
                fielders = re.findall(r'\((.*?)\)', advance)
                for f in fielders:
                    if f[-1] == position:
                        self.put_out += 1
                    elif position in list(f[:-1]):
                        self.assist += 1

        self.inning_at_position = (self.out_played + self.strike_out + self.pick_off + self.caught_stealing) / 3.0

        self.total_chance = self.put_out + self.assist + self.error
        if self.total_chance > 0:
            self.fielding = (self.put_out + self.assist) / self.total_chance

    def print_stats(self):
        header = ['INN', 'TC', 'PO', 'A', 'E', 'DP', 'PB', 'SB', 'CS', 'F']
        str_header = ['{:5s}'.format(h) for h in header]
        print('\t'.join(str_header))

        data = [
            self.inning_at_position,
            self.total_chance,
            self.put_out,
            self.assist,
            self.error,
            self.double_play,
            self.passed_ball,
            self.stolen_base,
            self.caught_stealing,
            self.fielding,
        ]
        str_data = ['{:<5d}'.format(d) if type(d) is int else '{:5.3f}'.format(d) for d in data]
        print('\t'.join(str_data))


class Player:
    def __init__(self, player_id, cursor, year=None, month=None, day=None, game=None):
        self.id = player_id
        self.cursor = cursor
        self.year = year
        self.month = month
        self.day = day
        self.game = game

        self.batting = Batting()
        self.base_running = BaseRunning()
        self.pitching = Pitching()
        self.fielding = Fielding()

    def parse_batting(self):
        self.batting.reset()

        cmd = """
        SELECT
           eventID, gameID, theplay, baserunning
        FROM
           event
        WHERE
           batterID='{}'
        """.format(self.id)
        if self.year is not None:
            cmd += "AND theyear='{}'".format(self.year)

        for row in self.cursor.execute(cmd):
            gameID = row[1]
            # park = gameID[0:3]
            # year = gameID[3:7]
            month = gameID[7:9]
            day = gameID[9:11]
            game = gameID[11]
            # print('park: {}, year: {}, month: {}, day: {}'.format(park, year, month, day))
            match_month = self.month is None or month == self.month
            match_day = self.day is None or day == self.day
            match_game = self.game is None or game == self.game
            if match_month and match_day and match_game:
                play = row[2]
                base_running = row[3]
                self.batting.parse(play, base_running)
                # print(row)

    def parse_base_running(self):
        self.base_running.reset()

        cmd = """
        SELECT
           eventID, gameID, batterID, runner_1b, runner_2b, runner_3b, theplay, baserunning
        FROM
           event
        WHERE
           (runner_1b='{}' OR runner_2b='{}' OR runner_3b='{}')
        """.format(self.id, self.id, self.id)
        if self.year is not None:
            cmd += "AND theyear='{}'".format(self.year)

        for row in self.cursor.execute(cmd):
            gameID = row[1]
            # park = gameID[0:3]
            # year = gameID[3:7]
            month = gameID[7:9]
            day = gameID[9:11]
            game = gameID[11]
            # print('park: {}, year: {}, month: {}, day: {}'.format(park, year, month, day))
            match_month = self.month is None or month == self.month
            match_day = self.day is None or day == self.day
            match_game = self.game is None or game == self.game
            if match_month and match_day and match_game:
                batterID = row[2]
                # catch database errors where player is both a batter and runner
                if batterID != self.id:
                    runner_1b = row[3]
                    runner_2b = row[4]
                    runner_3b = row[5]
                    base_running = row[7]

                    if runner_1b == self.id and base_running.find('1-4') >= 0:
                        self.batting.run += 1

                    if runner_2b == self.id and base_running.find('2-4') >= 0:
                        self.batting.run += 1

                    if runner_3b == self.id and base_running.find('3-4') >= 0:
                        self.batting.run += 1

                    # print(row)

    def parse_pitching(self):
        cmd = """
        SELECT
           eventID, gameID, inning, vis_score, home_score, outs, theplay, baserunning
        FROM
           event
        WHERE
          pitcherID='{}'
        """.format(self.id)
        if self.year is not None:
            cmd += "AND theyear='{}'".format(self.year)

        for row in self.cursor.execute(cmd):
            gameID = row[1]
            # park = gameID[0:3]
            # year = gameID[3:7]
            month = gameID[7:9]
            day = gameID[9:11]
            game = gameID[11]
            # print('park: {}, year: {}, month: {}, day: {}'.format(park, year, month, day))
            match_month = self.month is None or month == self.month
            match_day = self.day is None or day == self.day
            match_game = self.game is None or game == self.game
            if match_month and match_day and match_game:
                inning = row[2]
                vis_score = row[3]
                home_score = row[4]
                outs = row[5]
                play = row[6]
                base_running = row[7]
                self.pitching.parse_match_up(play, base_running, inning, vis_score, home_score, outs)
                print(row)

    def parse_fielding(self):
        positions = [
            ('2', 'field_C_playerID'),
            ('3', 'field_1B_playerID'),
            ('4', 'field_2B_playerID'),
            ('5', 'field_3B_playerID'),
            ('6', 'field_SS_playerID'),
            ('7', 'field_LF_playerID'),
            ('8', 'field_CF_playerID'),
            ('9', 'field_RF_playerID')
        ]

        cmd = """
        SELECT
           eventID, gameID, inning, vis_score, home_score, outs, theplay, baserunning,
           field_C_playerID,
           field_1B_playerID, field_2B_playerID, field_3B_playerID,
           field_SS_playerID,
           field_LF_playerID, field_CF_playerID, field_RF_playerID
        FROM
           event
        WHERE
           (field_C_playerID='{}' OR
            field_1B_playerID='{}' OR field_2B_playerID='{}' OR field_3B_playerID='{}' OR
            field_SS_playerID='{}' OR
            field_LF_playerID='{}' OR field_CF_playerID='{}' OR field_RF_playerID='{}')
        """.format(*[self.id] * 8)
        if self.year is not None:
            cmd += "AND theyear='{}'".format(self.year)

        for row in self.cursor.execute(cmd):
            gameID = row[1]
            # park = gameID[0:3]
            # year = gameID[3:7]
            month = gameID[7:9]
            day = gameID[9:11]
            game = gameID[11]
            # print('park: {}, year: {}, month: {}, day: {}'.format(park, year, month, day))
            match_month = self.month is None or month == self.month
            match_day = self.day is None or day == self.day
            match_game = self.game is None or game == self.game
            if match_month and match_day and match_game:
                inning = row[2]
                vis_score = row[3]
                home_score = row[4]
                outs = row[5]
                play = row[6]
                base_running = row[7]
                # assume row[8:16] matches positions 2-9
                for idx, fielder in enumerate(row[8:16]):
                    if self.id == fielder:
                        pos = str(idx + 2)
                        self.fielding.parse_play(play, base_running, pos, inning, vis_score, home_score, outs)
                        print(row[0:8])
