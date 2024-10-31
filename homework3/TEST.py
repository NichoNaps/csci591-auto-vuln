from interpreter import Interpreter
from runner import parseSourceCode


# this uses the following example from in class
func_def = parseSourceCode(
"""
int f(int x, int y) {
    int z = 1 > 0;

    if (x > y) {
        x = x + y/ 5(5453453+54);
        y = x - y;
        x = x - y;

       
    }


    return 1;
}
""", 'f')

print(func_def)

res = Interpreter.startOnFunction(func_def)

res.plot()



