import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error


def split_train_test(excel_path, test_ratio):
    df = pd.read_excel(excel_path, sheetname="ZhihuLive").fillna(value=0)
    df = df[df['review_score'] > 0]
    print(df.describe())
    print("*" * 100)
    dataset = df.loc[:, ['duration', 'original_price',
                         'has_authenticated', 'gender',
                         'liked_num', 'seats_taken']]
    min_max_scaler = preprocessing.MinMaxScaler()
    dataset = min_max_scaler.fit_transform(dataset)
    dataset = pd.DataFrame(dataset)

    print(dataset.describe())
    print("*" * 10)
    labels = df.loc[:, ['review_score']]

    shuffled_indices = np.random.permutation(len(df))
    test_set_size = int(len(df) * test_ratio)
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]

    return dataset.iloc[train_indices], dataset.iloc[test_indices], \
           labels.iloc[train_indices], labels.iloc[test_indices]


def train_and_test_model(train, test, train_Y, test_Y):
    # model = Pipeline([('poly', PolynomialFeatures(degree=3)),
    #                   ('linear', LinearRegression(fit_intercept=False))])
    model = RidgeCV(alphas=[_ * 0.1 for _ in range(1, 1000, 1)])
    model.fit(train, train_Y)
    mae_lr = round(mean_absolute_error(test_Y, model.predict(test)), 4)
    rmse_lr = round(np.math.sqrt(mean_squared_error(test_Y, model.predict(test))), 4)
    print('===============The Mean Absolute Error of Lasso Regression Model is {0}===================='.format(mae_lr))
    print('===============The Root Mean Square Error of Linear Model is {0}===================='.format(rmse_lr))


if __name__ == '__main__':
    train_set, test_set, train_label, test_label = split_train_test("D:/ZhihuLive.xlsx", 0.2)
    train_and_test_model(train_set, test_set, train_label, test_label)
