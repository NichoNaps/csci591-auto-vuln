from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f(int x, int y) {

    if (x || y > x) {
        return 0;
    }

    return 1;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



