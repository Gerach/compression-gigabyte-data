#!/usr/bin/python3

import operator
import os
import time
import argparse
import gc

import multiprocessing
from multiprocessing import Pool

WORDS_SEPARATOR = '2'
CHUNK_SEPARATOR = b'\xff\xff'


def read_args():
    parser = argparse.ArgumentParser(description='Custom text compressor writen by Gerardas Martynovas')
    parser.add_argument('-f', type=str, metavar='<file path>', required=True, help='Path to target file')
    parser.add_argument('-o', type=str, metavar='<file path>', required=True, help='Path to output file directory')
    parser.add_argument('-e', action='store_true', help='Encode file')
    parser.add_argument('-d', action='store_true', help='Decode file')
    parser.add_argument('-c', type=int, help='Chunk size')
    parser.add_argument(
        '-p',
        type=int,
        help='Pool processes this tool is going to use. '
             'Recommended to set to your processor core amount for best results.'
    )
    args = parser.parse_args()

    if not os.path.exists(args.f):
        parser.error('File not found: {}'.format(args.f))

    if not (args.e or args.d):
        parser.error('Undefined action, one of following actions is required: -e -d')

    if args.e and args.d:
        parser.error('Both actions cannot be simultaneously processed: -e -d')

    if args.e:
        encoder = Huffman(args.p, args.c)
        encoder.encode(args.f, args.o)

    if args.d:
        decoder = Huffman(args.p, args.c)
        decoder.decode(args.f, args.o)


class Node:
    def __init__(self, created, probability, has_parent, letter=None, parent='', is_left=None):
        self.letter = letter
        self.is_left = is_left
        self.probability = probability
        self.has_parent = has_parent
        self.created = created
        self.parent = parent


class Huffman:
    def __init__(self, processing_cores, chunk_size):
        self.codes = None
        self.decoder = None
        self.frequencies = None
        self.text_len = 0
        self.words = None
        self.graph = []
        self.creation_time = 0
        self.processing_cores = multiprocessing.cpu_count()
        if processing_cores:
            self.processing_cores = processing_cores
        self.chunk_size = 10485760
        if chunk_size:
            self.chunk_size = chunk_size

    def create_node(self, probability, has_parent, letter=None, parent=None, is_left=None) -> Node:
        self.creation_time += 1

        return Node(self.creation_time, probability, has_parent, letter, parent, is_left)

    def is_graph_joined(self) -> bool:
        nodes_without_parents = 0

        for node in self.graph:
            if not node.parent:
                nodes_without_parents += 1

        return nodes_without_parents == 1

    def sort_nodes(self) -> None:
        self.graph.sort(key=operator.attrgetter('has_parent', 'probability', 'created'))

    def connect_all_nodes(self) -> None:
        print('Connecting graph nodes')
        start_time = time.time()
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
        print(time.time() - start_time)

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

    def get_probabilities(self, total_letters) -> dict:
        probabilities = {}

        for word in self.words:
            probabilities[word] = self.frequencies[word] / total_letters

        return probabilities

    def get_probabilities_sorted(self) -> list:
        total_letters = 0
        for word in self.frequencies:
            total_letters += self.frequencies[word]

        probabilities = self.get_probabilities(total_letters)

        return sorted(probabilities.items(), key=operator.itemgetter(1))

    def encode_one_symbol(self, symbol):
        return self.codes[symbol]

    def prepare_graph(self, file_path, frequencies=None, words=None):
        self.text_len = 0
        self.frequencies, self.words = frequencies, words
        if not frequencies or not words:
            start_time = time.time()
            print('Getting letter dictionary')
            self.frequencies = {}

            with open(file_path, 'r', encoding='utf8') as rf:
                while True:
                    chunk = rf.read(self.chunk_size)
                    self.text_len += len(chunk)
                    for letter in set(chunk):
                        if letter in self.frequencies:
                            self.frequencies[letter] += chunk.count(letter)
                        else:
                            self.frequencies[letter] = chunk.count(letter)
                    if not chunk:
                        break

            self.words = list(self.frequencies.keys())

            print(time.time() - start_time)
        self.graph = []

        self.creation_time = 0

        probabilities = self.get_probabilities_sorted()

        print('Creating initial graph')
        start_time = time.time()
        for word in probabilities:
            letter = word[0]
            probability = word[1]
            node = Node(0, probability, False, letter)
            self.graph.append(node)

        print(time.time() - start_time)
        self.connect_all_nodes()

    def encode(self, file_path, output_file_path) -> None:
        self.prepare_graph(file_path)
        dir_split = '/'
        if os.sys.platform == 'win32':
            dir_split = "\\"
        file_name = file_path.split(dir_split)[-1]
        file_name_wo_ext = file_name.split('.', 1)[0]
        file_name_output = '{}{}{}.gm'.format(output_file_path, dir_split, file_name_wo_ext)

        c_time = os.path.getctime(file_path)
        m_time = os.path.getmtime(file_path)

        properties = '{} {} {} '.format(file_name, c_time, m_time)

        print('Writing document properties')
        with open(file_name_output, 'wb') as wf:
            wf.write(properties.encode())

        print('Writing encoder...')
        start_time = time.time()
        self.codes = self.get_all_codes()
        with open(file_name_output, 'ab') as wf:
            for letter in self.codes:
                wf.write(letter.encode())
                wf.write(self.codes[letter].encode())
                wf.write(WORDS_SEPARATOR.encode())
            wf.write(CHUNK_SEPARATOR)
        print(time.time() - start_time)

        print('Writing encoded data...')
        start_time = time.time()
        with open(file_path, 'r', encoding='utf8') as rf:
            for _ in range(0, self.text_len, self.chunk_size):
                bits = '1'
                chunk = rf.read(self.chunk_size)

                pool = Pool(self.processing_cores)
                bits += ''.join(pool.map(self.encode_one_symbol, chunk))

                with open(file_name_output, 'ab') as wf:
                    wf.write(int(bits, 2).to_bytes(len(bits) // 8 + 1, 'little'))
                    wf.write(CHUNK_SEPARATOR)
                gc.collect()
            print(time.time() - start_time)

    @staticmethod
    def read_properties(data_stream):
        f_bytes = data_stream.read(1)
        while ' ' not in f_bytes.decode():
            f_bytes += data_stream.read(1)
        return f_bytes.decode()

    def read_decoder(self, file_path):
        self.decoder = {}
        properties = {}

        print('Reading data...')
        start_time = time.time()
        with open(file_path, 'rb') as rf:
            properties['f_name'] = self.read_properties(rf).strip()
            properties['f_created'] = float(self.read_properties(rf))
            properties['f_modified'] = float(self.read_properties(rf))

            # letter - code
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
                elif decoded_byte != WORDS_SEPARATOR:
                    code += decoded_byte
                else:
                    lc.append(code)
                    code = ''

                if len(lc) == 2:
                    self.decoder[lc[1]] = lc[0]
                    lc.clear()

            data_in_bytes = rf.read()
            data_chunks = data_in_bytes.split(b'\xff\xff')

            print(time.time() - start_time)

            return properties, data_chunks

    def decode_chunk(self, chunk):
        bits = format(int.from_bytes(chunk, 'little'), 'b')[1:]

        data = ''
        coded_symbol = ''
        for bit in bits:
            coded_symbol += bit
            if coded_symbol in self.decoder:
                data += self.decoder[coded_symbol]
                coded_symbol = ''

        return data

    def decode(self, file_path, output_file_path) -> None:
        start_time = time.time()
        data = ''
        properties, chunks = self.read_decoder(file_path)
        output_file = '{}/{}'.format(output_file_path, properties['f_name'])

        print('Decoding...')
        pool = Pool(self.processing_cores)
        data += ''.join(pool.map(self.decode_chunk, chunks))

        with open(output_file, 'w', encoding='utf8') as wf:
            wf.write(data)
        os.utime(output_file, (properties['f_created'], properties['f_modified']))

        print(time.time() - start_time)


if __name__ == "__main__":
    read_args()
