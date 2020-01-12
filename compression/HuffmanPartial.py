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
# Optimal size for one chunk, this value brings best results
PARTIAL_CHUNK_SIZE = 9000


def read_args() -> None:
    """
    This function handles command line interface

    :return:
    """
    parser = argparse.ArgumentParser(description='Custom text compressor writen by Gerardas Martynovas')
    parser.add_argument('-f', type=str, metavar='<file path>', required=True, help='Path to target file')
    parser.add_argument('-o', type=str, metavar='<file path>', required=True, help='Path to output file directory')
    parser.add_argument('-e', action='store_true', help='Encode file')
    parser.add_argument('-d', action='store_true', help='Decode file')
    parser.add_argument('-c', type=int, help='Chunk size')
    parser.add_argument(
        '-p',
        type=int,
        help='Pool processes this tool is going to use.'
    )
    args = parser.parse_args()

    if not os.path.exists(args.f):
        parser.error('File not found: {}'.format(args.f))

    if not (args.e or args.d):
        parser.error('Undefined action, one of following actions is required: -e -d')

    if args.e and args.d:
        parser.error('Both actions cannot be simultaneously processed: -e -d')

    if args.e:
        encoder = HuffmanPartial(args.p, args.c)
        encoder.encode(args.f, args.o)
        return

    if args.d:
        decoder = HuffmanPartial(args.p, args.c)
        decoder.decode(args.f, args.o)
        return


class Node:
    """
    Node object represents a single node in either binary graph or disjoint graph context

    Properties
    ----------
    letter : str, optional
        represents a single symbol
    is_left : bool, optional
        if node is connected to parent, notes if it is left or right children to that parent
    probability : float
        has probability for leafs and accumulated probability for all other nodes
    has_parent : bool
        notes if node is connected to parent node
    created : int
        some point in time node was created represented by integer
    parent : Node, optional
        parent node object
    """
    def __init__(self, created, probability, has_parent, letter=None, parent='', is_left=None):
        """
        Node constructor

        :param created: int
        :param probability: float
        :param has_parent: bool
        :param letter: str
        :param parent: Node
        :param is_left: bool
        """
        self.letter = letter
        self.is_left = is_left
        self.probability = probability
        self.has_parent = has_parent
        self.created = created
        self.parent = parent


class HuffmanPartial:
    """
    Huffman algorithm with coding logic for partial document

    Properties
    ----------
    codes : dict
        has values of calculated huffman codes by symbol
    decoder : dict
        has values of decoded symbols by huffman code
    frequencies : dict
        has values of symbol frequencies by symbol
    text_len : int
        total raw input file length
    words : list
        list of unique symbols in raw input
    graph : Node[]
        all node objects in one array
    creation_time : int
        holds last used time point of node creation
    processing_cores : int
        count of processors used in parallel code execution
    chunk_size : int
        size of one chunk being processed at a time
    """
    def __init__(self, processes, chunk_size):
        """
        HuffmanPartial constructor

        :param processes: int
        :param chunk_size: int
        """
        self.codes = None
        self.decoder = None
        self.frequencies = None
        self.text_len = 0
        self.words = None
        self.graph = []
        self.creation_time = 0
        # default processors used in program equals to cpu cores available in system
        self.processes = multiprocessing.cpu_count()
        if processes:
            self.processes = processes
        # default chunk size of 10MB optimized for huge file compression
        self.chunk_size = 10485760
        if chunk_size:
            self.chunk_size = chunk_size

    def create_node(self, probability, has_parent, letter=None, parent=None, is_left=None) -> Node:
        """
        Creates and returns Node object

        :param probability: float
        :param has_parent: bool
        :param letter: str
        :param parent: Node
        :param is_left: bool
        :return: Node
        """
        self.creation_time += 1

        return Node(self.creation_time, probability, has_parent, letter, parent, is_left)

    def is_graph_joined(self) -> bool:
        """
        Returns true if graph is joint, false if disjoint

        :return: bool
        """
        nodes_without_parents = 0

        for node in self.graph:
            if not node.parent:
                nodes_without_parents += 1

        return nodes_without_parents == 1

    def sort_nodes(self) -> None:
        """
        Sorts all nodes in graph by following order:
            - node has parent
            - probability of node
            - crated time point

        :return: None
        """
        self.graph.sort(key=operator.attrgetter('has_parent', 'probability', 'created'))

    def connect_all_nodes(self) -> None:
        """
        Connect all nodes in graph until joint binary tree is present

        :return: None
        """
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
        """
        Recursively get huffman code for a single symbol

        :param node: Node
        :param code: str
        :return: str
        """
        if node.parent:
            if node.is_left:
                code += '1'
            else:
                code += '0'

            return self.get_code(node.parent, code)

        return code

    def get_letter_code(self, symbol) -> str:
        """
        Get huffman code for given symbol

        :param symbol: str
        :return: str
        """
        for node in self.graph:
            if node.letter == symbol:
                return self.get_code(node)[::-1]

    def get_all_codes(self) -> dict:
        """
        Get huffman codes for all known symbols

        :return: dict
        """
        codes = {}

        for word in self.words:
            code = self.get_letter_code(word)
            if not code:
                code = '0'
            codes[word] = code

        return codes

    def get_probabilities(self, total_letters) -> dict:
        """
        Get probabilities per symbol

        :param total_letters: int
        :return: dict
        """
        probabilities = {}

        for word in self.words:
            probabilities[word] = self.frequencies[word] / total_letters

        return probabilities

    def get_probabilities_sorted(self) -> list:
        """
        Get probabilities per symbol sorted by probability

        :return: list
        """
        total_letters = 0
        for word in self.frequencies:
            total_letters += self.frequencies[word]

        probabilities = self.get_probabilities(total_letters)

        return sorted(probabilities.items(), key=operator.itemgetter(1))

    def encode_one_symbol(self, symbol) -> str:
        """
        Returns huffman code for a single symbol

        :param symbol: str
        :return: str
        """
        return self.codes[symbol]

    def all_symbols_used(self, all_codes) -> bool:
        """
        Returns true if given codes contains all symbols known from raw input file

        :param all_codes: dict
        :return: bool
        """
        for letter in self.words:
            if letter not in all_codes.keys():
                return False
        return True

    @staticmethod
    def compare_codes(compare_to, compare) -> bool:
        """
        Returns true if every symbol in compare_to and compare match in length, returns false otherwise

        :param compare_to: dict
        :param compare: dict
        :return: bool
        """
        for symbol in compare:
            c_len = len(compare[symbol])
            ct_len = len(compare_to[symbol])

            if c_len != ct_len:
                return False
        return True

    def prepare_graph(self, file_path) -> None:
        """
        Calculates huffman codes for given file

        :param file_path: str
        :return: None
        """
        self.text_len = 0
        print('Preparing huffman codes...')
        start_time = time.time()
        self.frequencies = {}
        words = set()
        current_codes = None

        # get all unique symbols
        with open(file_path, 'r', encoding='utf8') as rf:
            while True:
                chunk = rf.read(self.chunk_size)
                if not chunk:
                    break
                self.text_len += len(chunk)
                words = words.union(set(chunk))
            self.words = list(words)

        # calculate codes for whole file
        with open(file_path, 'r', encoding='utf8') as rf:
            while True:
                self.graph = []
                self.creation_time = 0
                # read one chunk
                chunk = rf.read(PARTIAL_CHUNK_SIZE)
                if not chunk:
                    break
                for letter in set(chunk):
                    if letter in self.frequencies:
                        self.frequencies[letter] += chunk.count(letter)
                    else:
                        self.frequencies[letter] = chunk.count(letter)

                # calculate codes for one chunk
                try:
                    probabilities = self.get_probabilities_sorted()
                except KeyError:
                    continue
                for word in probabilities:
                    letter = word[0]
                    probability = word[1]
                    node = Node(0, probability, False, letter)
                    self.graph.append(node)

                # check if code lengths differ
                self.connect_all_nodes()
                codes = self.get_all_codes()
                if current_codes:
                    are_similar = self.compare_codes(current_codes, codes)
                    if are_similar:
                        print(time.time() - start_time)
                        return

                current_codes = codes

        self.connect_all_nodes()
        print(time.time() - start_time)

    def encode(self, file_path, output_file_path) -> None:
        """
        Encodes given input file with huffman codes and writes it to given output

        :param file_path: str
        :param output_file_path: str
        :return: None
        """
        self.prepare_graph(file_path)
        print('Encoding...')
        start_time = time.time()
        dir_split = '/'
        if os.sys.platform == 'win32':
            dir_split = "\\"
        file_name = file_path.split(dir_split)[-1]
        file_name_wo_ext = file_name.split('.', 1)[0]
        file_name_output = '{}{}{}.gm'.format(output_file_path, dir_split, file_name_wo_ext)

        c_time = os.path.getctime(file_path)
        m_time = os.path.getmtime(file_path)

        properties = '{} {} {} '.format(file_name, c_time, m_time)

        # write document data into file
        with open(file_name_output, 'wb') as wf:
            wf.write(properties.encode())

        # write decoder into file
        self.codes = self.get_all_codes()
        with open(file_name_output, 'ab') as wf:
            for letter in self.codes:
                wf.write(letter.encode())
                wf.write(self.codes[letter].encode())
                wf.write(WORDS_SEPARATOR.encode())
            wf.write(CHUNK_SEPARATOR)

        # write encoded data into file
        with open(file_path, 'r', encoding='utf8') as rf:
            for _ in range(0, self.text_len, self.chunk_size):
                bits = '1'
                chunk = rf.read(self.chunk_size)

                pool = Pool(self.processes)
                bits += ''.join(pool.map(self.encode_one_symbol, chunk))

                with open(file_name_output, 'ab') as wf:
                    wf.write(int(bits, 2).to_bytes(len(bits) // 8 + 1, 'little'))
                    wf.write(CHUNK_SEPARATOR)
                gc.collect()
        print(time.time() - start_time)

    @staticmethod
    def read_properties(data_stream) -> str:
        """
        Gets a single document property from encoded file data stream

        :param data_stream: BufferedReader
        :return: str
        """
        f_bytes = data_stream.read(1)
        while ' ' not in f_bytes.decode():
            f_bytes += data_stream.read(1)
        return f_bytes.decode()

    def read_decoder(self, file_path):
        """
        Reads decoder and encoded data chunks from given file

        :param file_path: str
        :return: dict, ByteArray
        """
        self.decoder = {}
        properties = {}

        with open(file_path, 'rb') as rf:
            properties['f_name'] = self.read_properties(rf).strip()
            properties['f_created'] = float(self.read_properties(rf))
            properties['f_modified'] = float(self.read_properties(rf))

            # lc stands for letter and code
            lc = []
            code = ''

            # Read encoded document byte by byte and read decoder
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

            # Read encoded data
            data_in_bytes = rf.read()
            data_chunks = data_in_bytes.split(b'\xff\xff')

            return properties, data_chunks

    def decode_chunk(self, chunk) -> str:
        """
        Decodes one chunk of encoded data

        :param chunk: ByteArray
        :return: str
        """
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
        """
        Decodes given input file and writes data to given output directory

        :param file_path: str
        :param output_file_path: str
        :return: None
        """
        start_time = time.time()
        data = ''
        properties, chunks = self.read_decoder(file_path)
        output_file = '{}/{}'.format(output_file_path, properties['f_name'])

        print('Decoding...')
        pool = Pool(self.processes)
        data += ''.join(pool.map(self.decode_chunk, chunks))

        with open(output_file, 'w', encoding='utf8') as wf:
            wf.write(data)
        os.utime(output_file, (properties['f_created'], properties['f_modified']))

        print(time.time() - start_time)


if __name__ == "__main__":
    read_args()
