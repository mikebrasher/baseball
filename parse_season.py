import csv
from os import listdir
from os.path import isfile, join
import sqlite3
import time


def main():
    # get all the {year}rs.csv files from the data directory
    data_path = 'data/seasons'
    csv_list = [join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f))]

    # get the header from the first file, assume all headers are the same
    with open(csv_list[0]) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        # remove second duplicate instance of 'play_orig'
        play_orig_index = [idx for idx, col in enumerate(header) if col == 'play_orig']
        play_orig_index = play_orig_index[-1]
        header.pop(play_orig_index)
        column_count = len(header)

    # connect to database and get cursor
    con = sqlite3.connect("seasons.db")
    cur = con.cursor()

    # drop event table if it already exists
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name='event'"
    res = cur.execute(cmd)
    event_exists = res.fetchone() is not None
    print('event exists: {}'.format(event_exists))
    if event_exists:
        reparse_database = False
        if reparse_database:
            cmd = 'DROP TABLE event'
            cur.execute(cmd)
        else:
            print('event table already exists, exiting')
            return

    # create new event table
    cmd = 'CREATE TABLE event({})'.format(', '.join(header))
    cur.execute(cmd)

    # insert each csv file into the event database
    tic = time.time()
    for rs in csv_list:
        print('inserting {}'.format(rs))
        with open(rs) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # pop header
            data = []
            for row in reader:
                row.pop(play_orig_index)
                assert len(row) == column_count
                data.append(tuple(row))
            # use placeholders '?' to avoid sql injection attacks
            cmd = 'INSERT INTO event VALUES({})'.format(', '.join(['?'] * column_count))
            cur.executemany(cmd, data)
            con.commit()
    toc = time.time()

    # inserted all csv files in 144.3937029838562 s
    print('inserted all csv files in {} s'.format(toc - tic))


if __name__ == "__main__":
    main()
