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
        self.assertEqual('KCA202206070', self.dataset.game_list[game_index])
        x, y = self.dataset[game_index]
        self.assertTrue(torch.is_tensor(x))

        num_player = 18
        self.assertEqual(num_player, x.shape[0])
        self.assertEqual(self.dataset.num_feature, x.shape[1])

        valid_game_results = [0, 1]
        self.assertIn(y, valid_game_results)

    def test_get_item(self):
        data = []
        for idx in range(len(self.dataset)):
            x, y = self.dataset[idx]
            data.append(x.flatten())
        data = torch.stack(data)

        actual_mu = data.mean(dim=0)
        actual_std = data.std(dim=0)
        self.assertEqual(len(actual_mu), len(actual_std))
        tol = 1e-3
        for idx in range(len(actual_mu)):
            self.assertAlmostEqual(0.0, float(actual_mu[idx]), delta=tol)
            if actual_std[idx] > tol:
                self.assertAlmostEqual(1.0, float(actual_std[idx]), delta=tol)
            else:
                self.assertAlmostEqual(0.0, float(actual_std[idx]), delta=tol)

    def test_get_items(self):
        features = []
        width = 1000
        lo = 0
        hi = min(lo + width, len(self.dataset))
        while lo < len(self.dataset):
            items = self.dataset.__getitems__(range(lo, hi))
            for x, y in items:
                features.append(x)
            lo += width
            hi = min(lo + width, len(self.dataset))
        data = torch.stack(features)
        data = data.flatten(1, -1)

        actual_mu = data.mean(dim=0)
        actual_std = data.std(dim=0)
        self.assertEqual(len(actual_mu), len(actual_std))
        tol = 1e-3
        for idx in range(len(actual_mu)):
            self.assertAlmostEqual(0.0, float(actual_mu[idx]), delta=tol)
            if actual_std[idx] > tol:
                self.assertAlmostEqual(1.0, float(actual_std[idx]), delta=tol)
            else:
                self.assertAlmostEqual(0.0, float(actual_std[idx]), delta=tol)

    def test_fetch_all_data(self):
        features, labels = self.dataset.fetch_all_data()
        data = features.flatten(1, -1)

        actual_mu = data.mean(dim=0)
        actual_std = data.std(dim=0)
        self.assertEqual(len(actual_mu), len(actual_std))
        tol = 1e-3
        for idx in range(len(actual_mu)):
            self.assertAlmostEqual(0.0, float(actual_mu[idx]), delta=tol)
            if actual_std[idx] > tol:
                self.assertAlmostEqual(1.0, float(actual_std[idx]), delta=tol)
            else:
                self.assertAlmostEqual(0.0, float(actual_std[idx]), delta=tol)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)


if __name__ == '__main__':
    unittest.main()
