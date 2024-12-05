import argparse
from pathlib import Path


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='run',description='')
    parser.add_argument('analysis', choices=['reaching', 'signed'], help='flow analysis mode')
    parser.add_argument('path', type=Path, help='specify path to w3a program')  

    args = parser.parse_args()


    print(args.analysis, args.path)

    #@TODO