import unittest
import torch
import os
from baseball.pipeline import Pipeline
from baseball.utils import BaseballDataset


class TestBaseballDataset(unittest.TestCase):

    def setUp(self):
        self.db_file = 'test_2022.db'
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        p = Pipeline()
        p.db_file = self.db_file
        p.lo_year = p.hi_year = 2022  # just process 2022
        p.process()
        self.dataset = BaseballDataset(self.db_file)

    def test_valid(self):
        # how many games in 2022
        self.assertEqual(2430, len(self.dataset))

        game_index = 1000
        self.assertEqual('BOS202206200', self.dataset.game_list[game_index])
        x, y = self.dataset[game_index]
        self.assertTrue(torch.is_tensor(x))

        num_player = 18
        self.assertEqual(num_player, x.shape[0])
        self.assertEqual(self.dataset.num_feature, x.shape[1])

        valid_game_results = [0, 1]
        self.assertIn(y, valid_game_results)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)


if __name__ == '__main__':
    unittest.main()
