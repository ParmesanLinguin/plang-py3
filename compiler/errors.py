from typing import NamedTuple
from sys import stdout
from nodes import ParseTreeNode

class Position(NamedTuple):
    index: int

    start_row: int
    start_col: int

    end_row: int
    end_col: int

class LineError(NamedTuple):
    message: str
    file: str
    line: str

    pos: Position

def write_single_err(err: LineError):
    write = stdout.write
    write(red + "error" + reset + ": " + err.message + "\n")
    write(italics + "--  in " + err.file + reset + "(" + green + str(err.pos.start_row) + reset + ":" + green + str(err.pos.start_col) + reset + "-" + green + str(err.pos.start_row) + reset + ":" + green + str(err.pos.end_col) + reset + ")\n")

    spaces = " " * len(err.line)
    length = (err.pos.end_col - err.pos.start_col)
    writestr = spaces[:err.pos.start_col - 1] + ("^" * length) + spaces[err.pos.end_col + length + 1:]
    line_no_size = len(str(err.pos.start_row))
    padding = "  "

    write(bg_white + " " + line_no_size * " " + " " + reset + padding  + "\n")
    write(bg_white + " " + black + str(err.pos.start_row) + " " + reset + padding + err.line + "\n")
    write(bg_white + " " + line_no_size * " " + " " + reset + padding + writestr)
    write("\n")

def get_whole_line(string: str, index: int):
    start: int = index
    end: int = index

    while start > 0 and string[start] != "\n":
        start -= 1
    
    while end < len(string) and string[end] != "\n":
        end += 1

    return string[start : end]

def construct_line(node):
    from lexer import Token
    tokens: list['Token'] = []
    content: str = ""
    current = node

    done = False
    while current.left and not done:
        token = current.left
        tokens.insert(0, token)

        for i, c in enumerate(reversed(token.content)):
            if c == "\n":
                done = True
                break
            else:
                content = c + content

        current = token

    current = node
    while True:
        token = current

        tokens.append(token)

        for c in token.content:
            if c == "\n":
                return content
            else:
                content = content + c

        if not token.right:
            return content

        current = token.right

    # string = ""

    # for i, (t, c) in enumerate(zip(tokens, content)):
    #     if i == len(tokens):
    #         string += t.content
    #         return string

    #     for char in c:
    #         if char == "\n":
    #             string = ""
    #             continue
    #         c += char

    # return string

__escape = "\u001b"
black = __escape + "[30m"
red = __escape + "[31m"
green = __escape + "[32m"
yellow = __escape + "[33m"
blue = __escape + "[34m"
magenta = __escape + "[35m"
cyan = __escape + "[36m"
white = __escape + "[37m"
italics = __escape + "[3m"

bg_white = __escape + "[47m"
reset = __escape + "[0m"