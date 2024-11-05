from interpreter import Interpreter
from runner import parseSourceCode




func_def = parseSourceCode(
"""
int f(int y) {
    int x = 0;
    y = y + run();

    while (x < 3) {
        x++;
    }

    // this should simplify to y < 3
    if (y < x) { 
        return 1;
    
    }

    return 0;
}
""", 'f')

res = Interpreter.startOnFunction(func_def)

res.plot()



