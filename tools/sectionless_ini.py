import os
import ConfigParser
import sys
import argparse

"""
Recently at work I had deal with ini files without sections and some files without starting/first section. Also had to
deal with different mix of interpolation(values can be preprocessed before returning them from get()), extensions. I
found solution by combining multiple threads from stackoverflow so keeping it in my tools.
"""

class SectionLessINI:
    def __init__(self, file_path):
        print ("Processing file: {}".format(file_path))

def parse_args():
    return 0

def main():
    return 0

if __name__ == "__main__":
    main()

    # s = SectionLessINI(file_path)