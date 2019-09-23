#!/usr/bin/python3

from Entropy import Entropy


class Huffman:
    def __init__(self):
        entropy = Entropy()
        entropy.fill_frequencies()
        probabilities = entropy.get_probabilities_sorted()
        self.graph = []
        self.created = 0

        while probabilities:
            try:
                # parent node init
                parent_node = self.create_node(self.created)

                # leaf 1 init
                letter1 = probabilities[0][0]
                probability1 = probabilities[0][1]
                node1 = self.create_node(self.created, True, letter1, probability1, parent_node)
                probabilities.remove(probabilities[0])

                # leaf 2 init
                letter2 = probabilities[0][0]
                probability2 = probabilities[0][1]
                node2 = self.create_node(self.created, False, letter2, probability2, parent_node)
                probabilities.remove(probabilities[0])

                # graph population
                parent_node.probability = probability1 + probability2
                self.graph.append(parent_node)
                self.graph.append(node1)
                self.graph.append(node2)
            except IndexError:
                letter = probabilities[0][0]
                probability = probabilities[0][1]
                node = Node(0, True, letter, probability)
                probabilities.remove(probabilities[0])
                self.graph.append(node)
                # TODO: add additional logic when there are not even number of letters

    def create_node(self, created, is_left=None, letter=None, probability=None, parent=None):
        self.created += 1

        return Node(created, is_left, letter, probability, parent)

    def connect_tree(self):
        nodes_without_parents = []

        for node in self.graph:
            if not node.parent:
                nodes_without_parents.append(node)

        if len(nodes_without_parents) < 2:
            return

        count = 0
        for _ in nodes_without_parents[::2]:
            parent_node = self.create_node(self.created)
            node1 = nodes_without_parents[count]
            node2 = nodes_without_parents[count + 1]
            node1.parent = parent_node
            node1.is_left = True
            node2.parent = parent_node
            node2.is_left = False
            parent_node.probability = node1.probability + node2.probability
            self.graph.append(parent_node)

            count += 2

        self.connect_tree()

    def get_code(self, node, code=''):
        if node.parent:
            if node.is_left:
                code += '0'
            else:
                code += '1'

            return self.get_code(node.parent, code)

        return code

    def get_letter_code(self, letter):
        for node in self.graph:
            if node.letter == letter:
                return self.get_code(node)

    def print_all_codes(self):
        for letter in Entropy.alphabet:
            code = self.get_letter_code(letter)
            print('{} - {}'.format(letter, code))


class Node:
    def __init__(self, created, is_left=None, letter=None, probability=None, parent=None):
        self.letter = letter
        self.is_left = is_left
        self.probability = probability
        self.created = created
        self.parent = parent


def main():
    huffman = Huffman()
    huffman.connect_tree()
    huffman.print_all_codes()


if __name__ == "__main__":
    main()
