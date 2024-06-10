import sqlite3
from player import Player


def main():
    # connect to database and get cursor
    con = sqlite3.connect("seasons.db")
    cur = con.cursor()

    # determine if event table exists
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name='event'"
    res = cur.execute(cmd)
    event_exists = res.fetchone() is not None
    if not event_exists:
        return

    # mookie = Player('bettm001', cur)
    # mookie.parse_batting()
    # mookie.batting.print_stats()

    # alcantara = Player('alcas001', cur, year='2022')
    # alcantara.parse_pitching()
    # alcantara.pitching.print_stats()

    swanson = Player('swand001', cur, year='2022')
    swanson.parse_fielding()
    swanson.fielding.print_stats()


if __name__ == "__main__":
    main()
