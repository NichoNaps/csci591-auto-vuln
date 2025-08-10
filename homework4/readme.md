# Introduction 
This is a data flow analysis tool written in python for the While3addr language. Data flow analysis is a useful static analysis tool in cyber security to find potential vulnerabilities in code without needing to run it like determining if customer data is being logged. We implemented the worklist algorithm for this data analysis tool allowing you to extend its functionality with different types of analysis. Included for this assignment are the following following analysis:
- **Integer Sign Analysis**: Determine at each point in the program whether an integer variable is positive, negative, or unknown
- **Reaching Definition Analysis**: Determine at each point in the program which variable assignments are active (uses subscripts to denote the line number where the assignment occurred).

See `logs/*` for examples of the program in action and `programs/*` for the While3addr programs used.

# Setup

```sh
# matplotlib is only needed for domain.py testing but networkx is required
pip install networkx matplotlib 
```

# Usage

```sh
python run.py -h # get help

# run a signed flow analysis
python run.py signed programs/prog_1.w3a 

# run a reaching flow analysis
python run.py reaching programs/prog_1.w3a 

```

# Layout
- `run.py` The file that takes command line args to run other code
- `worklist.py` The worklist algorithm 
- `reach_analysis.py` The reach analysis flow function and domain
- `int_sign_analysis.py` The signed analysis flow function and domain
- `test_zero_analysis.py` A test that implemented part of the zero analysis flow function and domain
- `domain.py` The domain/lattice joining code implemented using a networkx directed graph
- `parser.py` The code that parses the text of a While3Addr program



