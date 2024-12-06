import argparse
from pathlib import Path

from int_sign_analysis import run_int_sign_analysis
from reach_analysis import run_reach_analysis
from parser import Program

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='run',description='Data flow analysis tool for the while3addr programming language')
    parser.add_argument('analysis', choices=['reaching', 'signed'], help='flow analysis mode')
    parser.add_argument('path', type=Path, help='specify path to w3a program')  

    args = parser.parse_args()

    print(args.analysis, args.path)

    match args.analysis:
        case 'signed':
            run_int_sign_analysis(Program(args.path))
        case 'reaching':
            run_reach_analysis(Program(args.path))

    