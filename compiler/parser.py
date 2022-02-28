from typing import NoReturn
from errors import LineError, get_whole_line, write_single_err
from lexer import Token, TokenType
from nodes import ParseTreeNode, ParseTreeNodeType

class Parser:
    def __init__(self, tokens: list[Token], source: str):
        self.tokens = tokens
        self.position = 0
        self.source = source
        self.whitespace_buffer = []

        self.cur_tok = None
        self.next_tok = None

        self.last_tok = None

        if len(tokens) > 0:
            self.cur_tok = tokens[0]
            self.position += 1
        if len(tokens) > 1:
            self.next_tok = tokens[1]
            self.position += 1
        
        self.cur_tok = tokens[0] if len(tokens) > 0 else None
        self.next_tok = tokens[1] if len(tokens) > 1 else None

    def parse(self):
        return self.__parse_program()

    def __parse_program(self):
        nodes = []

        while True:
            nodes.append(self.__parse_function())

            if self.__accept(TokenType.EOF, nodes):
                break

        return ParseTreeNode(ParseTreeNodeType.Program, nodes)

    def __parse_function(self):
        if self.__peek_type() == TokenType.Kw_Imp:
            return self.__parse_imp_func()
        else:
            return self.__parse_pure_func()

    def __parse_imp_func(self):
        nodes = []

        self.__expect(TokenType.Kw_Imp, nodes)
        self.__expect(TokenType.Identifier, nodes)
        nodes.append(self.__parse_param_list())

        self.__expect(TokenType.Colon, nodes)
        self.__expect(TokenType.Identifier, nodes)
        nodes.append(self.__parse_block_expr())

        return ParseTreeNode(ParseTreeNodeType.ImpureFunction, nodes)
    
    def __parse_pure_func(self):
        nodes = []
    
        self.__accept(TokenType.Kw_Fun, nodes)
        self.__expect(TokenType.Identifier, nodes)
        nodes.append(self.__parse_param_list())

        self.__expect(TokenType.Colon, nodes)
        self.__expect(TokenType.Identifier, nodes)
        nodes.append(self.__parse_block_expr())

        return ParseTreeNode(ParseTreeNodeType.PureFunction, nodes)

    def __parse_param_list(self):
        nodes = []
        
        self.__expect(TokenType.LeftParen, nodes)
        if self.__accept(TokenType.Identifier, nodes):
            self.__expect(TokenType.Colon, nodes)
            self.__expect(TokenType.Identifier, nodes)

            while self.__accept(TokenType.Comma, nodes):
                self.__expect(TokenType.Identifier, nodes)
                self.__expect(TokenType.Colon, nodes)
                self.__expect(TokenType.Identifier, nodes)

        self.__expect(TokenType.RightParen, nodes)

        return ParseTreeNode(ParseTreeNodeType.ParamList, nodes)

    def __parse_expr(self):
        if self.__peek().type == TokenType.LeftBrace:
            return self.__parse_block_expr()
        else:
            return self.__parse_blockless_expr()

    # also parses statements
    def __parse_block_expr(self):
        nodes = []

        self.__expect(TokenType.LeftBrace, nodes)
        while not self.__accept(TokenType.RightBrace, nodes):
            nodes.append(self.__parse_expr())
            
            if self.__accept(TokenType.Semicolon, nodes):
                semi = nodes.pop()
                expr = nodes.pop()
                nodes.append(ParseTreeNode(ParseTreeNodeType.Statement, [expr, semi]))

        return ParseTreeNode(ParseTreeNodeType.BlockExpression, nodes)

    def __parse_blockless_expr(self):
        return ParseTreeNode(ParseTreeNodeType.BlocklessExpression, [self.__parse_term()], None)

    def __parse_term(self):
        nodes = []

        nodes.append(self.__parse_factor())

        while self.__accept([TokenType.Plus, TokenType.Minus], nodes):
            nodes.append(self.__parse_factor())

        return ParseTreeNode(ParseTreeNodeType.Term, nodes)

    def __parse_factor(self):
        nodes = []

        nodes.append(self.__parse_elem())

        while self.__accept([TokenType.Asterisk, TokenType.Slash], nodes):
            nodes.append(self.__parse_elem())

        return ParseTreeNode(ParseTreeNodeType.Factor, nodes)

    def __parse_elem(self):
        nodes = []

        if self.__accept(TokenType.Integer, nodes):
            return ParseTreeNode(ParseTreeNodeType.Element, nodes)
        elif self.__accept(TokenType.Identifier, nodes):
            if self.__peek_type() == TokenType.LeftParen:
                return self.__parse_function_call(nodes[0])
            else:
                return ParseTreeNode(ParseTreeNodeType.Element, nodes)
        else:
            self.__expect([TokenType.Integer, TokenType.Identifier])

    def __parse_function_call(self, identifier = None):
        nodes = []

        if identifier is None:
            self.__expect(TokenType.Identifier, nodes)

        nodes.append(self.__parse_arg_list())

    def __parse_arg_list(self):
        nodes = []

        self.__expect(TokenType.LeftParen, nodes)

        if not self.__accept(TokenType.RightParen, nodes):
            nodes.append(self.__parse_expr())

            while not self.__accept(TokenType.RightParen, nodes):
                self.__expect(TokenType.Comma, nodes)
                nodes.append(self.__parse_expr())

        return ParseTreeNode(ParseTreeNodeType.ArgumentList, nodes)

    def __expect(self, tok_type: TokenType | list[TokenType], into: list[ParseTreeNode] | None = None) -> bool | NoReturn:
        if type(tok_type) == TokenType:
            tok_type = [ tok_type ]
        
        self.__consume_whitespace()

        if self.__peek_type() in tok_type:
            if into is not None:
                self.__accept(self.__peek_type(), into)
            return True

        joined = self.__join([str(t) for t in tok_type])
        peeked = self.__peek()
        write_single_err(LineError(f"Expected token of type {joined}, encountered token of type {peeked.type}",
            peeked.source, get_whole_line(self.source, peeked.position.start_col), peeked.position))
        
        raise Exception(f"Expected token of type {joined}, but got token of type {self.__peek_type()}")

    def __accept(self, tok_type: TokenType | list[TokenType], into: list[ParseTreeNode]) -> bool:
        if type(tok_type) == TokenType:
            l = [ tok_type ]
        else:
            l: list[TokenType] = tok_type

        self.__consume_whitespace()

        for t in l:
            if self.__peek_type() == t:
                into.append(self.__consume_token())
                return True
        
        return False

    def __peek(self):
        return self.cur_tok

    def __peek_type(self):
        return self.__peek().type

    def __consume_token(self):
        buf = self.whitespace_buffer
        self.whitespace_buffer = []
        cur = self.__consume()
        return ParseTreeNode(ParseTreeNodeType.Token, buf, cur)

    def __consume_whitespace(self):
        while self.__peek_type() == TokenType.Whitespace:
            cur = self.__consume()
            token = ParseTreeNode(ParseTreeNodeType.Whitespace, [], cur)
            self.whitespace_buffer.append(token)

    @staticmethod
    def __join(list: list) -> str:
        return  ", ".join(t for t in list[:-1]) + ("," if len(list) > 2 else "") + (" or " if len(list) > 1 else "") + list[-1]

    def __consume(self):
        if self.cur_tok is None:
            raise Exception("Cannot consume null token")
        out_tok = self.cur_tok
        self.last_tok = out_tok
        self.cur_tok = self.next_tok
        self.next_tok = self.tokens[self.position] if self.position < len(self.tokens) else None
        self.position += 1

        return out_tok