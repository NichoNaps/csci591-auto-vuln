from interpreter import Interpreter
from runner import parseSourceCode




source_code = """
int f() {
    int x = 0;

    if (x++) {
        // Can't enter enter because x = 0
    }

    if (x) {
        // Must enter because x = 1
    }

    x--;

    if (x) {
        // Can't enter enter because x = 0
    }

    if (++x) {
        // Must enter because x = 1
    }


    return 1;
}
"""

func_def = parseSourceCode(source_code, 'f')

res = Interpreter.startOnFunction(func_def)

res.plot(source_code)



