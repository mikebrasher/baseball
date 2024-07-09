import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
import sqlite3


class BaseballDataset(Dataset):
    def __init__(self, db_file):
        self.db_file = db_file

        # connect to database and get cursor
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        cmd = 'SELECT * FROM game'
        self.game_list = []
        for row in self.cursor.execute(cmd):
            game_id = row[0]
            self.game_list.append(game_id)

        cmd = 'SELECT * FROM player'
        first_row = self.cursor.execute(cmd).fetchone()
        self.feature_index = 3
        self.num_feature = len(first_row[self.feature_index:])

    def __len__(self):
        return len(self.game_list)

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError

        cmd = 'SELECT * FROM game WHERE game_id=?'
        row = self.cursor.execute(cmd, [self.game_list[index]]).fetchone()
        game_id = row[0]
        # game_datetime = row[1]
        # vis_score = row[2]
        # home_score = row[3]
        label = row[4]
        starting_lineup = row[5:]

        # get features for every starting player
        cmd = """
            SELECT
                *
            FROM
                player
            WHERE
                game_id=?
        """
        feature_dict = {}
        for row in self.cursor.execute(cmd, [game_id]):
            player_id = row[0]
            assert row[1] == game_id
            feature_dict[player_id] = row[self.feature_index:]

        # preserve player order
        features = []
        for player_id in starting_lineup:
            features.append(feature_dict[player_id])
        features = torch.tensor(features)

        return features, label

    def __del__(self):
        if self.connection:
            self.connection.close()


def load_data(db_file, num_workers=0, batch_size=128):
    dataset = BaseballDataset(db_file)
    return DataLoader(dataset, num_workers=num_workers, batch_size=batch_size, shuffle=True, drop_last=True)


if __name__ == '__main__':
    bd = BaseballDataset('../data/features.db')

    seed = 12345
    rng = np.random.default_rng(seed)

    num_test = 5
    for i in rng.choice(len(bd), num_test):
        x, y = bd[i]
        print('x: {}'.format(x))
        print('y: {}'.format(y))
