class Parser:

    def __init__(self, filepath):
        self.filepath = filepath
    def parse_line(self, line):
        # Strip whitespace and remove the line number and colon '1:'
        line = line.strip()
        if ":" in line:
            line = line.split(":", 1)[1].strip()

        # Check if line is empty
        if not line:
            return None

        # Assignment: x := y op z
        # do we need to support (x := op z op x op i) or just one op? This currently supports one op
        if ":=" in line:
            parts = line.split(":=")
            left = parts[0].strip()
            right = parts[1].strip()
            # Check if operations exist
            if any(op in right for op in ["+", "-", "*", "/"]):
                # If operations exist, split it
                for op in ["+", "-", "*", "/"]:
                    if op in right:
                        operands = right.split(op)
                        return ("assign_op", left, operands[0].strip(), op, operands[1].strip())
            else:
                # x := y without op, it can be a number
                try:
                    right = int(right)
                    return ("assign_num", left, right)
                except ValueError:
                    return ("assign_var", left, right)

        # Goto: goto n
        elif line.startswith("goto"):
            target = int(line.split()[1])
            return ("goto", target)

        # Conditional goto: if x op 0 goto n
        # Example: if x < 0 goto 5
        elif line.startswith("if"):
            parts = line.split("goto")
            # Remove "if" from left part
            left = parts[0][3:].strip()
            target = int(parts[1].strip())
            for op in ["<", "="]:  # Only < and = are valid operators
                if op in left:
                    operand = left.split(op)
                    return ("if_goto", operand[0].strip(), op, operand[1].strip(), target)

        # Halt statement
        elif line == "halt":
            return ("halt",)

        else:
            raise ValueError(f"ERROR: {line}")


    def parse_program(self):
        filepath = self.filepath
        with open(filepath, "r") as file:
            lines = file.readlines()

        instructions = []
        for line_num, line in enumerate(lines, start=1):
            try:
                parsed = self.parse_line(line)
                if parsed:
                    instructions.append((line_num, parsed))
            except ValueError as e:
                print(f"ERROR {line_num}: {e}")

        return instructions


# Example usage
if __name__ == "__main__":

    # Parse the program
    parser = Parser("programs/prog_4.w3a")
    result = parser.parse_program()
    # result = parse_program("programs/prog_4.w3a")
    for line_num, instruction in result:
        print(f"Line {line_num}: {instruction}")
