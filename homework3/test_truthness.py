from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f(int x, int y) {

    if (5 && 3) {

    }

    if (x + y / 2 > 0) {

    }

  

    return 1;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



