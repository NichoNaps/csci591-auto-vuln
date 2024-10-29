from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f(int x, int y) {
    int z = 5;

    if (x > y) {
        int x = x;

        x = x + y;
        y = x - y;
        x = x - y;

        if (1 == 1) {
            int x = 5;
            return 0;
        }
    }


    return 1;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



