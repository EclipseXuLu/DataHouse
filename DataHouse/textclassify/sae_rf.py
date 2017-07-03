import os
import shutil

import gensim
import jieba
import jieba.analyse
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfTransformer, HashingVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.neural_network import MLPClassifier

TEXT_DIR = '/home/lucasx/Desktop/corpus_6_4000/'
FEATURE_NUM = 30
STOPWORDS_FILE = 'stopwords.txt'
USER_DICT = 'userdict.txt'


def get_all_categories(dir_):
    category_list = []
    for _ in os.listdir(dir_):
        category = _.split('_')[0].strip()
        if category not in category_list:
            category_list.append(category)

    return category_list


def init_train_and_test_dataset(dir_, category_list):
    training_data_ratio = 0.7
    dataset = {
        'name': 'dataset'
    }
    training_set = {
    }

    test_set = {
    }

    category_num = {}
    for category in category_list:
        if category == 'Military':
            category_num[category] = 0
        elif category == 'Culture':
            category_num[category] = 1
        elif category == 'Economy':
            category_num[category] = 2
        elif category == 'Sports':
            category_num[category] = 3
        elif category == 'Auto':
            category_num[category] = 4
        else:
            category_num[category] = 5
        dataset[category_num[category]] = [os.path.join(dir_, _) for _ in os.listdir(dir_) if category in _]

    for category, num in category_num.items():
        training_set[num] = dataset[num][0: int(len(dataset[num]) * training_data_ratio)]
        test_set[num] = dataset[num][int(len(dataset[num]) * training_data_ratio): len(dataset[num])]

    return training_set, test_set


def get_stopwords(stopwords_filepath):
    """
    read stopwords and return as a python list
    :param stopwords_filepath:
    :return:
    """
    with open(stopwords_filepath, mode='rt', encoding='UTF-8') as f:
        stopwords = f.readlines()
        f.close()

    return stopwords


def documents_to_tfidf_vec(documents):
    """
    convert the document text list into the TF-IDF feature matrix X
    :param documents:
    :return:
    """
    transformer = TfidfTransformer(smooth_idf=True)
    hasher = HashingVectorizer(n_features=FEATURE_NUM,
                               stop_words=get_stopwords(STOPWORDS_FILE), non_negative=True,
                               norm=None, binary=False)
    vectorizer = make_pipeline(hasher, transformer)
    X = vectorizer.fit_transform(documents)

    return X


def read_document_from_text(text_filepath):
    """
    read document content from txt file
    :param text_filepath:
    :return:
    """
    with open(text_filepath, mode='rt') as f:
        document = ''.join(f.readlines())
        f.close()

    return document


if __name__ == '__main__':
    category_list = get_all_categories(TEXT_DIR)
    training_set, test_set = init_train_and_test_dataset(TEXT_DIR, category_list)

    training_text = []
    training_label = []
    test_text = []
    test_label = []
    for label, filepath_list in training_set.items():
        training_text += [read_document_from_text(_) for _ in filepath_list]
        training_label += [label for _ in range(len(filepath_list))]

    for label, filepath_list in test_set.items():
        test_text += [read_document_from_text(_) for _ in filepath_list]
        test_label += [label for _ in range(len(filepath_list))]

    train_X = documents_to_tfidf_vec(training_text)
    test_X = documents_to_tfidf_vec(test_text)

    print('=' * 100)
    print('start launching MLP Classifier......')
    mlp = MLPClassifier(solver='lbfgs', alpha=1e-4, hidden_layer_sizes=(50, 30, 30, 20), random_state=1)
    mlp.fit(train_X, training_label)
    print('finish launching MLP Classifier, the test accuracy is {:.5%}'.format(mlp.score(test_X, test_label)))
