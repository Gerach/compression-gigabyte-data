#!/usr/bin/python3
import operator

from Entropy import Entropy
from ExtractFromPdf import ExtractFromPdf


class Node:
    def __init__(self, created, probability, has_parent, letter=None, parent='', is_left=None):
        self.letter = letter
        self.is_left = is_left
        self.probability = probability
        self.has_parent = has_parent
        self.created = created
        self.parent = parent


class Huffman:
    def __init__(self, frequencies, words):
        entropy = Entropy(frequencies, words)
        probabilities = entropy.get_probabilities_sorted()
        self.words = words
        self.graph = []
        self.creation_time = 0

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
        while not self.is_graph_joined():
            node1 = self.graph[0]
            node2 = self.graph[1]

            parent_probability = node1.probability + node2.probability
            parent_node = self.create_node(parent_probability, False)
            self.graph.append(parent_node)

            node1.parent = parent_node
            node2.parent = parent_node
            node1.has_parent = True
            node2.has_parent = True

            if node1.probability > node2.probability:
                node1.is_left = True
                node2.is_left = False
            else:
                node1.is_left = False
                node2.is_left = True

            self.sort_nodes()

        for i in self.graph:
            print('{} {} {} {}'.format(i.letter, i.probability, i.has_parent, i.created))

    def get_code(self, node, code='') -> str:
        if node.parent:
            if node.is_left:
                code += '0'
            else:
                code += '1'

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
            codes[word] = code

        return codes


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    dictionary = extractor.get_letter_dictionary()
    alphabet = extractor.get_alphabet()

    huffman = Huffman(dictionary, alphabet)
    huffman.connect_all_nodes()
    codes = huffman.get_all_codes()
    codes = sorted(codes.items(), key=operator.itemgetter(1))
    for code in codes:
        print(code)


if __name__ == "__main__":
    main()
