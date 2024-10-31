from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f() {
    int x = 0;

    while (x < 3) {
        x = x + 1;
    }

    int z = 5;

    return 1;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



