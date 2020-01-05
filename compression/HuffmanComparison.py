#!/usr/bin/python3

import operator

from Huffman import Huffman
from ExtractFromPdf import ExtractFromPdf

import time

dvibalsiai = [
    'ai',
    'au',
    'ei',
    'ui',
    'ie',
    'uo',
]


def calculate_average(huffman, codes) -> float:
    total_words = sum(huffman.frequencies.values())
    total_coding_bits = 0
    total_bits = 0

    for code in codes:
        bits_per_code = len(code[0].encode('utf-8'))
        bits_per_encoded_word = len(code[1])
        words_per_encoded_code = huffman.frequencies[code[0]]
        total_coding_bits += bits_per_code + bits_per_encoded_word + 16
        total_bits += bits_per_encoded_word * words_per_encoded_code

    return (total_bits + total_coding_bits) / total_words


def get_word_dictionary(text, symbols=1):
    dictionary = {}

    if symbols == 0:
        for dvibalsis in dvibalsiai:
            if dvibalsis in text:
                word_count = text.count(dvibalsis)
                text = text.replace(dvibalsis, '')
                dictionary[dvibalsis] = word_count
        symbols = 1

    while text:
        word = text[0:symbols]
        word_count = text.count(word)
        text = text.replace(word, '')
        dictionary[word] = word_count

    alphabet = list(dictionary.keys())

    return dictionary, alphabet


file_name = '../file_manipulation/random_10.txt'

huffman = Huffman()
with open(file_name, 'r', encoding='utf8') as rf:
    data = rf.read()

freq, words = get_word_dictionary(data, 0)
huffman.prepare_graph(file_name, freq, words)
codes = huffman.get_all_codes()
codes = sorted(codes.items(), key=operator.itemgetter(1))
avg_bits_per_word = calculate_average(huffman, codes)
print('LT\t{}'.format(avg_bits_per_word))
print(len(words))

for s_count in range(1, 10):
    then = time.time()
    freq, words = get_word_dictionary(data, s_count)
    huffman.prepare_graph(file_name, freq, words)
    codes = huffman.get_all_codes()
    codes = sorted(codes.items(), key=operator.itemgetter(1))
    # for code in codes:
    #     print('{} {}'.format(code, dictionary[code[0]]))
    avg_bits_per_word = calculate_average(huffman, codes)
    # print('bits required to encode {} symbol(s): {}; average bits per symbol: {}'
    #       .format(s_count, avg_bits, avg_bits/s_count)
    #       )
    # symbols count \tab bits per symbol
    print('{}\t{}\t{}\t{}'.format(s_count, avg_bits_per_word / s_count, len(words), time.time() - then))
