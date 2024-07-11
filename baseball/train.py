from baseball.utils import load_data
import torch
import xgboost as xgb
import multiprocessing
import time

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def eval_accuracy(data, model):
    correct = 0
    count = 0
    for x_test, y_test in data:
        d_test = xgb.DMatrix(x_test.flatten(1, -1))

        y_prob = model.predict(d_test)
        for p, label in zip(y_prob, y_test):
            predict = 1 if p > 0.5 else 0
            if predict == label:
                correct += 1
            count += 1

    return correct / count


def train_xgboost():
    seed = 1234
    torch.manual_seed(seed)

    tic = time.time()
    train_data = load_data('../data/train.db', batch_size=1024)  # 177911
    toc = time.time()
    print('loaded train data in {} seconds'.format(toc - tic))

    valid_data = load_data('../data/valid.db', batch_size=1024)  # 2429
    test_data = load_data('../data/test.db', batch_size=1024)  # 2430

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
        'gamma': 10,  # min split loss
        'eta': 0.01,  # learning rate
        'subsample': 0.4,
        'min_child_weight': 10,
        'objective': 'binary:logistic',
        'nthread': multiprocessing.cpu_count(),
        'eval_metric': 'logloss',
    }
    # eval_list = [(d_train, 'train'), (d_valid, 'eval')]

    max_epoch = 2
    model = None
    for epoch in range(max_epoch):
        batch_idx = 0
        for x, y in train_data:
            print('training batch {}'.format(batch_idx))
            batch_idx += 1
            d_train = xgb.DMatrix(x.flatten(1, -1), label=y)
            model = xgb.train(params, d_train)
        acc_valid = eval_accuracy(valid_data, model)
        print('epoch: {}, valid accuracy: {}'.format(epoch, acc_valid))

    # test model
    tic = time.time()
    acc_test = eval_accuracy(test_data, model)
    print('test accuracy: {}'.format(acc_test))
    toc = time.time()
    print('evaluated test accuracy in {} seconds'.format(toc - tic))


if __name__ == '__main__':
    train_xgboost()
