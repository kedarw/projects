import os
import configparser
import sys
import argparse
import io

"""
Recently at work I had to deal with ini files without sections and some files without starting/first section. Also had
to deal with different mix of interpolation(values can be preprocessed before returning them from get()), extensions. I
found solution by combining multiple threads from stackoverflow so keeping it in my tools.
"""

class SectionLessINI:
    def __init__(self, file_path):
        print ("Processing file: {}".format(file_path))
        self.file_path = file_path

def parse(self):
    try:
        config = configparser.ConfigParser()
        config.read(self.file_path)

        print("\nIni file contents:")

        for section in config.sections():
            print(section)
            for (key, value) in config.items(section):
                print(key, value)

    except configparser.MissingSectionHeaderError:
        file_with_dummy_root = '[root]\n' + open(self.file_path).read()
        fp = io.StringIO(file_with_dummy_root)
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read_file(fp)

        for section in config.sections():
                        print(section)

        for (key, value) in config.items(section):
                            print(key, value)
    finally:
        if not fp.closed:
            fp.close()

def main():
    return 0

if __name__ == "__main__":
    s = SectionLessINI(os.path.join(os.path.dirname(__file__), "sample.cfg"))
    s.parse()