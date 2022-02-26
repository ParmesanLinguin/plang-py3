import traceback
from errors import write_single_err, LineError, Position
from lexer import Lexer, TokenType
from nodes import ParseTreeNode, ParseTreeNodeType
from parser import Parser
from plast import FunctionDecl, Program, Statement, parse_tree_to_ast, Node, BinaryOperation

def main() -> None:
    while True:
        source = input("Enter an expression to parse:\n")
        try:
            l = Lexer(source, "input")
            tokens = l.lex()
        except Exception as e:
            traceback.print_exception(e)
            break

        for token in tokens:
            print(token)

        try:
            parser = Parser(tokens, source)
            p_root = parser.parse()
            print_root(p_root, "", True)

            ast_root = parse_tree_to_ast(p_root)
            print_root(ast_root, "", True)
        except Exception as e:
            traceback.print_exception(e)
            break

def print_root(root: ParseTreeNode | Node, indent: str, last: bool):
    print(indent, end="")
    print("\\-" if last else "|-", end="")
    indent += "  " if last else "| "

    if type(root) == ParseTreeNode:
        print(root.type if not root.type == ParseTreeNodeType.Token else f"{root.token.type} {root.token.content}")

        children = list(filter(lambda c: c.type != ParseTreeNodeType.Whitespace, root.children))
        for i, c in enumerate(children):
            print_root(c, indent + "  ", i == len(children) - 1)
    else:
        t = type(root)

        if t == BinaryOperation:
            print(t.op)
            print_root(t.left, indent + "  ", False)
            print_root(t.right, indent + "  ", True)

        elif t == Program:
            print("Program")
            
            for i, c in enumerate(root.children):
                print_root(c, indent + "  ", i == len(root.children) - 1)

        elif t == Statement:
            print("Statement")
            print_root(root.child, indent + "  ", True)

        elif t == FunctionDecl:
            str1 = f"{('fun' if not root.pure or root.pure.type == TokenType.Kw_Pure else 'imp')} {root.name}"
            str2 = "(" + ", ".join([f'{p.name}: {p.type}' for p in root.parameters]) + ")"
            print(str1 + str2)
            print_root(root.body, indent + "  ", True)

        else:
            print("not implemented")

if __name__ == "__main__":
    main()
