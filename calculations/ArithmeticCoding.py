#!/usr/bin/python3

import fractions

from ExtractFromPdf import ExtractFromPdf


class ArithmeticCoding:

    def __init__(self):
        self.interval_start = {}
        self.width = {}

    def calc_intervals(self, symbol_counts, message_length) -> None:
        start_interval = fractions.Fraction(0, message_length)

        for letter in symbol_counts:
            self.interval_start[letter] = start_interval
            self.width[letter] = fractions.Fraction(symbol_counts[letter], message_length)
            start_interval = start_interval + self.width[letter]

    def encode(self, message, message_length) -> str:
        start = fractions.Fraction(0, message_length)
        width = fractions.Fraction(message_length, message_length)

        for letter in message:
            start += self.interval_start[letter] * width
            width *= self.width[letter]

        end = start + width

        bin_fraction = fractions.Fraction()
        power = 1
        while True:
            if start <= bin_fraction < end:
                break

            numerator = (start.numerator * power) // start.denominator + 1
            bin_fraction = fractions.Fraction(numerator, power)

            power *= 2

        numerator_binary = bin(bin_fraction.numerator)
        return numerator_binary

    def decode(self, message, message_length) -> str:
        numerator = int(message, 2)
        denominator_bin = '0b1' + '0' * (len(message) - 2)
        denominator = int(denominator_bin, 2)
        input_fraction = fractions.Fraction(numerator, denominator)
        output = ''

        while len(output) < message_length:
            for letter in self.interval_start:
                if 0 <= input_fraction - self.interval_start[letter] < self.width[letter]:
                    input_fraction = (input_fraction - self.interval_start[letter]) / self.width[letter]
                    output += letter

        return output


def main():
    # extractor = ExtractFromPdf('Neris.pdf')
    # dictionary = extractor.get_letter_dictionary()
    # alphabet = extractor.get_alphabet()
    # total_symbols = extractor.get_length()

    dictionary = {
        '1': 1,
        '2': 1,
        '3': 2,
    }
    alphabet = ['1', '2', '3']
    text = '3123'
    coding = ArithmeticCoding()
    coding.calc_intervals(dictionary, len(text))
    encoded_message = coding.encode(text, len(text))
    print(encoded_message)
    decoded_message = coding.decode(encoded_message, len(text))
    print(decoded_message)


if __name__ == "__main__":
    main()
