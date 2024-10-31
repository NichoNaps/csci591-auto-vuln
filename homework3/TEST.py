from interpreter import Interpreter
from runner import parseSourceCode


# this uses the following example from in class
source_code = """
int f(int x, int y) {
    int z = 5;

    if (x > y) {
        x = x + y;
        y = x - y;
        x = x - y;

        if (x > y) {
            return 0;
        }
    }


    return 1;
}
"""

func_def = parseSourceCode(source_code, 'f')

print(func_def)

res = Interpreter.startOnFunction(func_def)

res.plot(source_code)



