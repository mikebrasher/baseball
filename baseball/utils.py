import torch
from torch.utils.data import Dataset, DataLoader
import sqlite3


class BaseballDataset(Dataset):
    def __init__(self, db_file):
        self.db_file = db_file

        # connect to database and get cursor
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        cmd = 'SELECT game_id FROM game'
        self.game_list = []
        for row in self.cursor.execute(cmd):
            game_id = row[0]
            self.game_list.append(game_id)

        cmd = 'SELECT * FROM game'
        first_row = self.cursor.execute(cmd).fetchone()
        self.feature_index = 5
        self.num_aggregate_feature = len(first_row[self.feature_index:])

        self.num_player = 18
        self.num_feature = self.num_aggregate_feature // self.num_player

        scaler_index = 2
        cmd = """SELECT * FROM scaler WHERE id=0 AND statistic='mu'"""
        row = self.cursor.execute(cmd).fetchone()
        self.mu = torch.tensor(row[scaler_index:])

        cmd = """SELECT * FROM scaler WHERE id=1 AND statistic='std'"""
        row = self.cursor.execute(cmd).fetchone()
        self.std = torch.tensor(row[scaler_index:])

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __len__(self):
        return len(self.game_list)

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError

        cmd = 'SELECT * FROM game WHERE game_id=?'
        game_id = self.game_list[index]
        row = self.cursor.execute(cmd, [game_id]).fetchone()
        assert row[0] == game_id
        # game_id = row[0]
        # game_datetime = row[1]
        # vis_score = row[2]
        # home_score = row[3]
        label = row[4]
        features = (torch.tensor(row[self.feature_index:]) - self.mu) / self.std
        features = features.reshape(self.num_player, self.num_feature)

        return features, label

    def __getitems__(self, index_list):
        game_id_list = [self.game_list[idx] for idx in index_list]

        cmd = 'SELECT * FROM game WHERE game_id IN ({})'.format(','.join(['?'] * len(game_id_list)))
        items = []
        for row in self.cursor.execute(cmd, game_id_list):
            assert row[0] in game_id_list
            # game_id = row[0]
            # game_datetime = row[1]
            # vis_score = row[2]
            # home_score = row[3]
            label = row[4]
            features = (torch.tensor(row[self.feature_index:]) - self.mu) / self.std
            features = features.reshape(self.num_player, self.num_feature)
            items.append((features, label))

        return items

    def fetch_all_data(self, max_count=None):
        feature_list = []
        label_list = []

        count = 0
        cmd = 'SELECT * FROM game'
        for row in self.cursor.execute(cmd):
            # game_id = row[0]
            # game_datetime = row[1]
            # vis_score = row[2]
            # home_score = row[3]
            label = row[4]
            label_list.append(label)
            features = (torch.tensor(row[self.feature_index:]) - self.mu) / self.std
            features = features.reshape(self.num_player, self.num_feature)
            feature_list.append(features)
            count += 1
            if max_count is not None and count >= max_count:
                break

        all_features = torch.stack(feature_list)
        all_labels = torch.tensor(label_list)

        return all_features, all_labels


def load_data(db_file, num_workers=0, batch_size=128):
    dataset = BaseballDataset(db_file)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        drop_last=True,
    )
