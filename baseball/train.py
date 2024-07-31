from baseball.utils import load_data
import numpy as np
import torch
import xgboost as xgb
import multiprocessing
import time

import matplotlib.pyplot as plt

# import cProfile
# import pstats
# import io

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class ConfusionMatrix:
    def __init__(self):
        self.threshold = 0.5
        self.true_positive = 0
        self.false_positive = 0
        self.true_negative = 0
        self.false_negative = 0
        self.correct = 0
        self.count = 0
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        self.f1 = 0.0

    def evaluate(self, y_prob, y_gold, threshold):
        self.true_positive = 0
        self.false_positive = 0
        self.true_negative = 0
        self.false_negative = 0
        self.threshold = threshold
        for p, label in zip(y_prob, y_gold):
            predict = 1 if p > threshold else 0
            if label.item() == 1:
                if predict == 1:
                    self.true_positive += 1
                else:
                    self.false_negative += 1
            else:
                if predict == 1:
                    self.false_positive += 1
                else:
                    self.true_negative += 1

        self.correct = self.true_positive + self.true_negative
        self.count = self.true_positive + self.false_positive + self.true_negative + self.false_negative
        assert self.count == len(y_gold)

        if self.count > 0:
            self.accuracy = self.correct / self.count
        else:
            self.accuracy = 0.0

        if self.true_positive + self.false_positive > 0:
            self.precision = self.true_positive / (self.true_positive + self.false_positive)
        else:
            self.precision = 0.0

        if self.true_positive + self.false_negative > 0:
            self.recall = self.true_positive / (self.true_positive + self.false_negative)
        else:
            self.recall = 0.0

        if self.precision + self.recall > 0.0:
            self.f1 = 2.0 * self.precision * self.recall / (self.precision + self.recall)
        else:
            self.f1 = 0.0

    def __str__(self):
        result = 'ConfusionMatrix:\n'
        result += '  true_positive: {}\n'.format(self.true_positive)
        result += '  false_positive: {}\n'.format(self.false_positive)
        result += '  true_negative: {}\n'.format(self.true_negative)
        result += '  false_negative: {}\n'.format(self.false_negative)
        result += '  correct: {}\n'.format(self.correct)
        result += '  count: {}\n'.format(self.count)

        return result


def eval_accuracy(d_eval, y_gold, model):
    y_prob = model.predict(d_eval)
    print('min(y_prob): {}'.format(y_prob.min()))
    print('max(y_prob): {}'.format(y_prob.max()))

    cm = ConfusionMatrix()
    cm.evaluate(y_prob, y_gold, threshold=0.8)
    print(cm)

    return cm.accuracy


def plot_loss(progress):
    train_loss = progress['train']['logloss']
    valid_loss = progress['valid']['logloss']
    rounds = range(len(train_loss))

    fig, ax = plt.subplots()
    ax.plot(rounds, train_loss, label='Train')
    ax.plot(rounds, valid_loss, label='Valid')
    ax.legend()
    plt.xlabel('num boost round')
    plt.ylabel('log-loss')
    plt.title('XGBoost Classification Loss')
    plt.show()


def plot_pr_curve(d_eval, y_gold, model):
    y_prob = model.predict(d_eval)
    count = len(y_prob)

    cm = ConfusionMatrix()

    num_threshold = 101
    min_threshold = y_prob.min()
    max_threshold = y_prob.max()
    dt = (max_threshold - min_threshold) / (num_threshold - 1)
    threshold = np.arange(min_threshold, max_threshold + dt, dt)
    precision = []
    recall = []
    f1 = []

    for t in threshold:
        cm.evaluate(y_prob, y_gold, threshold=t)
        precision.append(cm.precision)
        recall.append(cm.recall)
        f1.append(cm.f1)

    fig, ax = plt.subplots()
    ax.plot(threshold, precision, label='Precision')
    ax.plot(threshold, recall, label='Recall')
    ax.plot(threshold, f1, label='F1')
    plt.legend()
    plt.xlabel('Threshold (-)')
    plt.ylabel('Precision (-)')
    plt.title('PR Curve')
    plt.grid()
    plt.show()

    # fig, ax = plt.subplots()
    # s = ax.scatter(recall, precision, c=threshold, cmap='plasma')
    # # ax.colormap()
    # # ax.legend()
    # plt.colorbar(s)
    # plt.xlabel('Recall (-)')
    # plt.ylabel('Precision (-)')
    # plt.title('PR Curve')
    # plt.show()


def train_xgboost():
    seed = 1234
    torch.manual_seed(seed)

    # profile = cProfile.Profile()
    # profile.enable()

    tic = time.time()
    train_data = load_data('../data/train.db')  # 177911
    x_train, y_train = train_data.dataset.fetch_all_data(max_count=1000)
    d_train = xgb.DMatrix(x_train.flatten(1, -1), label=y_train)
    toc = time.time()
    print('loaded train data in {} seconds'.format(toc - tic))

    valid_data = load_data('../data/valid.db')  # 2429
    x_valid, y_valid = valid_data.dataset.fetch_all_data()
    d_valid = xgb.DMatrix(x_valid.flatten(1, -1), label=y_valid)

    test_data = load_data('../data/test.db')  # 2430
    x_test, y_test = test_data.dataset.fetch_all_data()
    d_test = xgb.DMatrix(x_test.flatten(1, -1), label=y_test)

    print('home win in test: {}'.format(sum(y_test) / len(y_test)))

    # tic = time.time()
    # x, y = next(iter(train_data))
    # d_train = xgb.DMatrix(x.flatten(1, -1), label=y)
    # toc = time.time()
    # print('loaded train batch in {} seconds'.format(toc - tic))

    # tic = time.time()
    # x, y = next(iter(valid_data))
    # d_valid = xgb.DMatrix(x.flatten(1, -1), label=y)
    # toc = time.time()
    # print('loaded valid data in {} seconds'.format(toc - tic))

    params = {
        'max_depth': 6,
        'gamma': 0,  # min split loss
        'eta': 0.1,  # learning rate
        'subsample': 1,
        'min_child_weight': 1,
        'objective': 'binary:logistic',
        'nthread': multiprocessing.cpu_count(),
        'eval_metric': 'logloss',
    }
    eval_list = [(d_train, 'train'), (d_valid, 'valid')]

    progress = {}
    model = xgb.train(params, d_train, num_boost_round=250, evals=eval_list, evals_result=progress)

    acc_valid = eval_accuracy(d_valid, y_valid, model)
    print('valid accuracy: {}'.format(acc_valid))

    # test model
    # tic = time.time()
    acc_test = eval_accuracy(d_test, y_test, model)
    print('test accuracy: {}'.format(acc_test))
    # toc = time.time()
    # print('evaluated test accuracy in {} seconds'.format(toc - tic))

    # plot_loss(progress)
    plot_pr_curve(d_test, y_test, model)

    # profile.disable()
    # stream = io.StringIO()
    # pstats.Stats(profile, stream=stream).sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
    # print(stream.getvalue())


if __name__ == '__main__':
    train_xgboost()
