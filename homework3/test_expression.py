from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f(int x, int y) {

    int z = 100 + myFunc();
    
    if (x + y / 2 > 0 && 1) {
        x = x + 2 * 7;
    }

    if (0) {}

    return 1;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



