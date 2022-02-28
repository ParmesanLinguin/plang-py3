import traceback
from errors import write_single_err, LineError, Position
from lexer import Lexer, TokenType
from nodes import ParseTreeNode, ParseTreeNodeType
from parser import Parser
from plast import FunctionDecl, Program, Statement, parse_tree_to_ast, Node, BinaryOperation, Expression, IntegerLiteral, Identifier
from validation import validate_ast
from time import perf_counter_ns

def main() -> None:
    while True:
        source = ""
        print("Enter an expression to parse:\n")
        while True:
            inpt = input("> ")
            if inpt == ".comp":
                break
            else:
                source += "\n" + inpt
        
        start = perf_counter_ns()
        print("\nLexing...")
        try:
            l = Lexer(source, "input")
            tokens = l.lex()
        except Exception as e:
            print("FAILED!")
            traceback.print_exception(e)
            break
        
        end = perf_counter_ns()

        print(f"DONE! {format_ns(end - start)}")
        print(f"\nParsing... ")

        start = perf_counter_ns()

        try:
            parser = Parser(tokens, source)
            p_root = parser.parse()

            ast_root = parse_tree_to_ast(p_root)

            validate_ast(ast_root)
        except Exception as e:
            print("\nFAILED!\n")
            traceback.print_exception(e)
            break
        
        end = perf_counter_ns()

        print(f"DONE! {format_ns(end - start)}")

def print_root(root: ParseTreeNode | Node, indent: str, last: bool):
    print(indent, end="")
    print("\\-" if last else "|-", end="")
    indent += "  " if last else "| "

    if type(root) == ParseTreeNode:
        name = root.type if not root.type == ParseTreeNodeType.Token else f"{root.token.type} {root.token.content}"
        
        print(name)

        children = list(filter(lambda c: c.type != ParseTreeNodeType.Whitespace, root.children))
        for i, c in enumerate(children):
            print_root(c, indent + "  ", i == len(children) - 1)
    else:
        t = type(root)

        if t == Program:
            print("Program")
            
            for i, c in enumerate(root.children):
                print_root(c, indent + "  ", i == len(root.children) - 1)

        elif t == Statement:
            print("Statement")
            print_root(root.child, indent + "  ", True)

        elif t == FunctionDecl:
            str1 = f"{('fun' if not root.pure or root.pure.token.type == TokenType.Kw_Fun else 'imp')} {root.name.token.content}"
            str2 = "(" + ", ".join([f'{p.name.value}: {p.type.value}' for p in root.parameters.params]) + ")"
            print(str1 + str2)
            print_root(root.body, indent + "  ", True)

        elif t == Expression:
            print("Expression")

            for i, c in enumerate(root.children):
                print_root(c, indent + "  ", i == len(root.children) - 1)

        elif t == BinaryOperation:
            print(f"BinaryOperation {root.op}")

            print_root(root.left, indent + "  ", False)
            print_root(root.right, indent + "  ", True)

        elif t == IntegerLiteral:
            print(f"Integer {root.value}")

        elif t == Identifier:
            print(f"Identifier {root.value}")
        else:
            print("not implemented")

def format_ns(time): 
    if time <= 1_000:
        return f"{time} ns"
    elif time > 1_000 and time <= 1_000_000:
        return f"{(time / 1_000):.2f} µs"
    elif time > 1_000_000 and time <= 1_000_000_000:
        return f"{(time / 1_000_000):.2f} ms"
    else:
        return f"{(time / 1_000_000_000):.2f} s"

if __name__ == "__main__":
    main()
