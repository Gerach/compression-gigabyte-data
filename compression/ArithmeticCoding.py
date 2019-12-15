#!/usr/bin/python3

import fractions
import re
import progressbar

from ExtractFromPdf import ExtractFromPdf


def calc_numerator(message) -> str:
    return re.sub(r'10*', '', message, 1)


def calc_denominator(message) -> str:
    output = '0b1'
    bits = len(message) - 2
    for bit in range(bits - 1):
        output += '0'

    return output


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
        print('Encoding message')
        bar = progressbar.ProgressBar(
            maxval=100,
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
        )
        bar.start()
        bar_counter = 0
        bar_increment = 100 / message_length

        start = fractions.Fraction(0, message_length)
        width = fractions.Fraction(message_length, message_length)

        for letter in message:
            bar_counter += bar_increment
            bar.update(bar_counter)
            start += self.interval_start[letter] * width
            width *= self.width[letter]

        end = start + width

        fraction = fractions.Fraction()
        denominator = 1
        while True:
            if start <= fraction < end:
                break

            numerator = ((start.numerator * denominator) // start.denominator) + 1
            fraction = fractions.Fraction(numerator, denominator)

            denominator *= 2

        fraction_xor = fraction.numerator ^ fraction.denominator
        numerator_binary = bin(fraction_xor)
        bar.finish()
        return numerator_binary

    def decode(self, message, message_length) -> str:
        print('Decoding message')
        bar = progressbar.ProgressBar(
            maxval=100,
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
        )
        bar.start()
        bar_counter = 0
        bar_increment = 100 / message_length

        numerator_adjusted = calc_numerator(message)
        denominator_adjusted = calc_denominator(message)
        numerator = int(numerator_adjusted, 2)
        denominator = int(denominator_adjusted, 2)
        input_fraction = fractions.Fraction(numerator, denominator)
        output = ''

        while len(output) < message_length:
            bar_counter += bar_increment
            bar.update(bar_counter)
            for letter in self.interval_start:
                if 0 <= input_fraction - self.interval_start[letter] < self.width[letter]:
                    input_fraction = (input_fraction - self.interval_start[letter]) / self.width[letter]
                    output += letter

        bar.finish()
        return output


def main():
    extractor = ExtractFromPdf('Neris.pdf')
    dictionary = get_letter_dictionary()
    total_symbols = extractor.get_length()
    text = extractor.get_words()
    coding = ArithmeticCoding()
    coding.calc_intervals(dictionary, total_symbols)
    encoded_message = coding.encode(text, total_symbols)
    print(encoded_message)
    print('average character size encoded: {} bits'.format(len(encoded_message) / total_symbols))
    decoded_message = coding.decode(encoded_message, total_symbols)
    print(decoded_message)


if __name__ == "__main__":
    main()
