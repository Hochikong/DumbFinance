# __author__ = 'Hochikong'
from __future__ import print_function, unicode_literals
from bosonnlp import BosonNLP
from jieba import load_userdict, posseg, add_word, del_word, enable_parallel, disable_parallel
from os import getenv

"""
This program used for NLP ops,you can use jieba_config() to configurate.And you can use BosonNLP NER service
with sen_ner(),but first you should use sen_cut() to create a input data.
"""


# Initial the BosonNLP instance
nlp = BosonNLP(getenv('BOSON_TOKEN'))


def jieba_config(
        userdict=None,
        config=None,
        wordlist=None,
        parallel=False,
        p=0):
    """
    Use load_userdict() to load your dict or use add_word add a word list or delete a word
    :param userdict: A list contains filename
    :param config: 'A' or 'D',add_word or del_word
    :param wordlist: A list contains specify word
    :param parallel: Configurate to enable multiprocessing
    :param p: Process number
    :return: A string
    """
    if userdict:
        for file in userdict:
            load_userdict(file)
    if config == 'A':
        if wordlist:
            for word in wordlist:
                add_word(word)
        else:
            return 'Wordlist require!'
    elif config == 'D':
        if wordlist:
            for word in wordlist:
                del_word(word)
        else:
            return 'Wordlist require!'
    else:
        return 'Invalid config content'
    if parallel:
        if p >= 0:
            enable_parallel(p)
        else:
            return 'Invalid p content'
    elif not parallel:
        disable_parallel()
    else:
        return 'Invalid parallel content'


def sen_cut(sentence):
    """
    Execute cut()
    :param sentence: A sentence
    :return: A list
    """
    words = posseg.cut(sentence)
    result = [{'word': [], 'tag':[]}]
    for word, flag in words:
        result[0]['word'].append(word)
        result[0]['tag'].append(flag)
    return result


def sen_ner(data, sensitivity=None, segmented=False):
    """
    Execute ner() remotely
    :param data: A list from sen_cut or a sentence
    :param sensitivity: A number
    :param segmented: False or True,True use
    :return: A list
    """
    sensitivity_list = [1, 2, 3, 4, 5]
    if segmented:
        if sensitivity in sensitivity_list:
            result = nlp.ner(data, sensitivity, True)
            return result
        else:
            return 'Invalid sensitivity content'
    else:
        if sensitivity in sensitivity_list:
            result = nlp.ner(data, sensitivity)
            return result
        else:
            return 'Invalid sensitivity content'
