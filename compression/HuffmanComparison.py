#!/usr/bin/python3

import operator

from ExtractFromPdf import ExtractFromPdf
from Huffman import Huffman


for s_count in range(1, 1000):
    extractor = ExtractFromPdf('Neris.pdf')
    dictionary = extractor.get_word_dictionary(s_count)
    alphabet = extractor.get_alphabet()

    huffman = Huffman(dictionary, alphabet)
    huffman.connect_all_nodes()
    codes = huffman.get_all_codes()
    codes = sorted(codes.items(), key=operator.itemgetter(1))
    # for code in codes:
    #     print('{} {}'.format(code, dictionary[code[0]]))
    avg_bits_per_word = huffman.calculate_average(codes, s_count)
    # print('bits required to encode {} symbol(s): {}; average bits per symbol: {}'
    #       .format(s_count, avg_bits, avg_bits/s_count)
    #       )
    print('{}\t{}'.format(s_count, avg_bits_per_word / s_count))
