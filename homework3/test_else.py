from interpreter import Interpreter
from runner import parseSourceCode


# this uses the following example from in class
source_code = """
int f(int x, int y) {

    if (x > y) {
        x = x + y;
        y = x - y;
        x = x - y;
    } else {
        int y = y++; // variable shadow
        x = y;

        return 5;
    }


    return 0;
}
"""


func_def = parseSourceCode(source_code, 'f')

print(func_def)

res = Interpreter.startOnFunction(func_def)

res.plot()



