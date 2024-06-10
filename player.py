import re


def parse_out(play):
    is_out = False
    put_out = []
    assist = []
    delim = '|'
    sub_play = re.sub(r'\([B1234]\)', delim, play)
    sub_play = sub_play.strip(delim)
    events = sub_play.split(delim)
    first = events[0]
    if first.isdigit():
        is_out = True
        for e in events:
            put_out.append(e[-1])
            assist += list(e[:-1])
    return is_out, put_out, assist


class Batting:
    def __init__(self):
        # at bat enum
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
        self.unknown = 0

        # derived stats
        self.run = 0
        self.hit = 0
        self.at_bat = 0
        self.run_batted_in = 0
        self.batting_average = 0.0
        self.on_base_percentage = 0.0
        self.slugging = 0.0

    def parse_at_bat(self, play, base_running):
        events = play.split('/')
        first = events[0]
        is_out, _, _ = parse_out(first)
        if is_out:
            if events[1] == 'SH':
                self.sacrifice_hit += 1
            elif events[1] == 'SF':
                self.sacrifice_fly += 1
            else:
                self.out += 1
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
            self.run += 1
            self.run_batted_in += 1
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
        else:
            self.unknown += 1

        self.hit = self.single + self.double + self.triple + self.home_run
        self.at_bat = self.hit + self.strike_out + self.out + self.error + self.fielders_choice

        # don't include ground into double play
        # don't include errors on fielding the hit
        # don't include wild pitches
        if 'GDP' not in events and first.find('E') < 0 and first.find('WP') < 0:
            # or on the play at home, i.e. '1-4(E6)'
            rbi_list = ['1-4', '2-4', '3-4']
            for advance in base_running.split(';'):
                if advance in rbi_list:
                    self.run_batted_in += 1

        # hits divided by at bats (H/AB)
        if self.at_bat > 0:
            self.batting_average = self.hit / self.at_bat

        #  times reached base (H + BB + HBP) divided by
        times_reached_base = self.hit + self.walk + self.hit_by_pitch
        #  at bats plus walks plus hit by pitch plus sacrifice flies (AB + BB + HBP + SF)
        at_bats_plus = self.at_bat + self.walk + self.hit_by_pitch + self.sacrifice_fly
        if at_bats_plus > 0:
            self.on_base_percentage = times_reached_base / at_bats_plus

        # total bases achieved on hits divided by at-bats (TB/AB)
        total_bases = self.single + 2 * self.double + 3 * self.triple + 4 * self.home_run
        if self.at_bat > 0:
            self.slugging = total_bases / self.at_bat

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
        is_out, put_out, _ = parse_out(first)
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
        # pitching even enum
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
        is_out, put_out, assist = parse_out(first)
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
                fielders = re.search(r'\((.*?)\)', advance).group(1)
                if fielders[-1] == position:
                    self.put_out += 1
                elif position in list(fielders[:-1]):
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
        self.pitching = Pitching()
        self.fielding = Fielding()

    def parse_at_bats(self):
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
                self.batting.parse_at_bat(play, base_running)
                # print(row)

    def parse_base_running(self):
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

    def parse_batting(self):
        self.parse_at_bats()
        self.parse_base_running()

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
