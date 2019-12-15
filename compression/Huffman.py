#!/usr/bin/python3

import operator
import math

from Entropy import Entropy


class Node:
    def __init__(self, created, probability, has_parent, letter=None, parent='', is_left=None):
        self.letter = letter
        self.is_left = is_left
        self.probability = probability
        self.has_parent = has_parent
        self.created = created
        self.parent = parent


def encode(text, codes) -> None:
    print('Encoding...')

    # save decoder to file
    with open('out_encoded.bin', 'wb') as wf:
        for letter in codes:
            wf.write(letter.encode())

            wf.write(codes[letter].encode())
            wf.write('2'.encode())

        wf.write(b'\xff\xff')

    # save data to file
    bits = '1'
    for symbol in text:
        bits += codes[symbol]

    size_in_bytes = math.ceil(len(bits) / 8)

    with open('out_encoded.bin', 'ab') as wf:
        wf.write(int(bits, 2).to_bytes(size_in_bytes, 'little'))


def decode() -> None:
    print('Decoding...')
    decoder = {}
    data = ''

    with open('out_encoded.bin', 'rb') as rf:
        lc = []
        code = ''

        while True:
            byte = rf.read(1)

            try:
                decoded_byte = byte.decode()
            except UnicodeDecodeError:
                second_byte = rf.read(1)
                if second_byte == b'\xff':
                    break
                decoded_byte = (byte + second_byte).decode()

            if not lc:
                lc.append(decoded_byte)
            elif decoded_byte != '2':
                code += decoded_byte
            else:
                lc.append(code)
                code = ''

            if len(lc) == 2:
                decoder[lc[1]] = lc[0]
                lc.clear()

        data_in_bytes = rf.read()
        bits = format(int.from_bytes(data_in_bytes, 'little'), 'b')[1:]

    coded_symbol = ''
    for bit in bits:
        coded_symbol += bit
        try:
            data += decoder[coded_symbol]
            coded_symbol = ''
        except KeyError:
            continue

    with open('out_decoded.txt', 'w', encoding='utf8') as wf:
        wf.write(data)


def get_letter_dictionary(text):
    print('Getting letter dictionary')
    letters = text
    dictionary = {}

    while text:
        letter = text[0]
        letter_count = text.count(letter)
        text = text.replace(letter, '')
        dictionary[letter] = letter_count

    alphabet = list(dictionary.keys())

    return dictionary, alphabet


class Huffman:
    def __init__(self, text):
        self.frequencies, self.words = get_letter_dictionary(text)
        self.graph = []
        self.creation_time = 0

        entropy = Entropy(self.frequencies, self.words)
        probabilities = entropy.get_probabilities_sorted()

        print('Creating initial graph')
        for word in probabilities:
            letter = word[0]
            probability = word[1]
            node = Node(0, probability, False, letter)
            self.graph.append(node)

    def create_node(self, probability, has_parent, letter=None, parent=None, is_left=None) -> Node:
        self.creation_time += 1

        return Node(self.creation_time, probability, has_parent, letter, parent, is_left)

    def is_graph_joined(self) -> bool:
        nodes_without_parents = 0

        for node in self.graph:
            if not node.parent:
                nodes_without_parents += 1
            if nodes_without_parents > 1:
                return False

        return True

    def sort_nodes(self):
        self.graph.sort(key=operator.attrgetter('has_parent', 'probability', 'created'))

    def connect_all_nodes(self):
        print('Connecting graph nodes')
        while not self.is_graph_joined():
            node1, node2 = self.graph[0], self.graph[1]
            parent_probability = node1.probability + node2.probability
            parent_node = self.create_node(parent_probability, False)
            self.graph.append(parent_node)

            node1.parent, node2.parent = parent_node, parent_node
            node1.has_parent, node2.has_parent = True, True

            if node1.probability > node2.probability:
                node1.is_left, node2.is_left = True, False
            else:
                node1.is_left, node2.is_left = False, True

            self.sort_nodes()

    def get_code(self, node, code='') -> str:
        if node.parent:
            if node.is_left:
                code += '1'
            else:
                code += '0'

            return self.get_code(node.parent, code)

        return code

    def get_letter_code(self, letter) -> str:
        for node in self.graph:
            if node.letter == letter:
                return self.get_code(node)[::-1]

    def get_all_codes(self) -> dict:
        codes = {}

        for word in self.words:
            code = self.get_letter_code(word)
            if not code:
                code = '0'
            codes[word] = code

        return codes

    def calculate_average(self, codes, letters_per_code) -> float:
        total_words = sum(self.frequencies.values())
        total_coding_size = 0
        total_bits = 0

        for code in codes:
            bits_per_encoded_word = len(code[1])
            total_coding_size += (8 * letters_per_code) + bits_per_encoded_word
            words_per_encoded_code = self.frequencies[code[0]]
            total_bits += bits_per_encoded_word * words_per_encoded_code

        return (total_bits + total_coding_size + 8) / total_words


def main():
    with open('../file_manipulation/random.txt', 'r', encoding='utf8') as rf:
        text = rf.read()

    huffman = Huffman(text)
    huffman.connect_all_nodes()
    # codes = huffman.get_all_codes()
    # codes = sorted(codes.items(), key=operator.itemgetter(1))
    # for code in codes:
    #     print('{} {}'.format(code, dictionary[code[0]]))
    # avg_bits = huffman.calculate_average(codes, 1)
    # print('average bits: {}'.format(avg_bits))
    encode(text, huffman.get_all_codes())
    decode()


if __name__ == "__main__":
    main()
