#!/usr/bin/python3

import operator

from ExtractFromPdf import ExtractFromPdf
from Huffman import Huffman


for s_count in [1, 2, 3, 4]:
    extractor = ExtractFromPdf('Neris.pdf')
    dictionary = extractor.get_word_dictionary(s_count)
    alphabet = extractor.get_alphabet()

    huffman = Huffman(dictionary, alphabet)
    huffman.connect_all_nodes()
    codes = huffman.get_all_codes()
    codes = sorted(codes.items(), key=operator.itemgetter(1))
    # for code in codes:
    #     print('{} {}'.format(code, dictionary[code[0]]))
    avg_bits = huffman.calculate_average(codes)
    print('average bits per {} symbol(s): {}'.format(s_count, avg_bits))
