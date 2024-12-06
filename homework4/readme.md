
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



