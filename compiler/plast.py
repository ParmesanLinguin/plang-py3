from collections import namedtuple
from typing import NamedTuple, TypeAlias
from lexer import TokenType, Token
from nodes import ParseTreeNodeType, ParseTreeNode

class BinaryOperation(NamedTuple):
    left: 'Node'
    right: 'Node'
    op: str

class Expression(NamedTuple):
    left_brace: 'AstToken | None'
    right_brace: 'AstToken | None'
    children: list['Node'] 
    type: 'None | LangType'

class Program(NamedTuple):
    children: list['Node']
    eof: 'AstToken'

class Statement(NamedTuple):
    child: 'Node'
    semi: 'AstToken'

class FunctionDecl(NamedTuple):
    pure: 'AstToken | None'
    name: 'AstToken'
    parameters: 'ParamList'
    type: 'TypeSpec'
    body: 'Expression'
    
class ParamList(NamedTuple):
    left_paren: 'AstToken'
    params: list['Param']
    right_paren: 'AstToken'

class Param(NamedTuple):
    name: 'AstToken'
    type: 'TypeSpec'
    comma: 'AstToken | None'

class FunctionCall(NamedTuple):
    name: 'AstToken'
    arguments: 'ArgList'

class ArgList(NamedTuple):
    left_paren: 'AstToken'
    args: list['Expression']
    right_paren: 'AstToken'

class TypeSpec(NamedTuple):
    type: 'Node'
    colon: 'AstToken'

class IntegerLiteral(NamedTuple):
    value: str
    token: 'AstToken'

class Identifier(NamedTuple):
    value: str
    token: 'AstToken'

class AstToken(NamedTuple):
    token: 'Token'
    whitespace: list['Token']

Node = BinaryOperation | Expression | Program | Statement | FunctionDecl | ParamList | Param | TypeSpec | AstToken

def parse_tree_to_ast(root: ParseTreeNode): 
    if root.type == ParseTreeNodeType.Program:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        return Program(nodes[:-1], nodes[-1])

    elif root.type == ParseTreeNodeType.BlockExpression:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        return Expression(nodes[0], nodes[-1], nodes[1:-1], None)

    elif root.type == ParseTreeNodeType.BlocklessExpression:
        return parse_tree_to_ast(root.children[0])

    elif root.type == ParseTreeNodeType.Statement:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        return Statement(nodes[0], nodes[1])

    elif root.type == ParseTreeNodeType.PureFunction or root.type == ParseTreeNodeType.ImpureFunction:
        nodes = [parse_tree_to_ast(c) for c in root.children]

        f_pure = nodes.pop(0) if nodes[0].token.type in [TokenType.Kw_Fun, TokenType.Kw_Imp] else None
        name = nodes.pop(0)
        p_list = nodes.pop(0)
        f_type = TypeSpec(nodes.pop(1), nodes.pop(0))
        body = nodes.pop(0)

        assert len(nodes) == 0, "nodes was not empty"

        return FunctionDecl(f_pure, name, p_list, f_type, body)

    elif root.type == ParseTreeNodeType.ParamList:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        lparen = nodes.pop(0)
        rparen = nodes.pop(-1)

        params = []

        while len(nodes) > 0:
            name = nodes.pop(0)
            p_type = TypeSpec(nodes.pop(1), nodes.pop(0))
            comma = nodes.pop(0) if len(nodes) > 0 else None

            params.append(Param(name, p_type, comma))

        return ParamList(lparen, params, rparen)

    elif root.type == ParseTreeNodeType.ArgumentList:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        lparen = nodes.pop(0)
        rparen = nodes.pop(-1)

        return ArgList(lparen, nodes, rparen)

    elif root.type == ParseTreeNodeType.Token:
        return AstToken(root.token, root.children)

    elif root.type == ParseTreeNodeType.Term or root.type == ParseTreeNodeType.Factor:
        cdn = root.children
        
        if len(cdn) == 1:
            return parse_tree_to_ast(cdn[0])
        
        nodes = list(map(lambda x: parse_tree_to_ast(x), cdn[::-2]))
        ops = list(reversed(cdn[1::2]))

        while len(nodes) > 1:
            nodes.append(BinaryOperation(nodes.pop(), nodes.pop(), ops.pop().token.content))

        return nodes.pop()

    elif root.type == ParseTreeNodeType.FunctionCall:
        nodes = [parse_tree_to_ast(c) for c in root.children]
        return FunctionCall(nodes[0], nodes[1])

    elif root.type == ParseTreeNodeType.Element:
        node = parse_tree_to_ast(root.children[0])

        if node.token.type == TokenType.Integer:
            return IntegerLiteral(node.token.content, node)

        elif node.token.type == TokenType.Identifier:
            return Identifier(node.token.content, node)

        else:
            raise Exception("Unreachable code")

    elif root.type == ParseTreeNodeType.Whitespace:
        pass

    else:
        raise NotImplementedError(f"Not implemented for type {root.type}")

