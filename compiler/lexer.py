from enum import Enum, auto, unique
from typing import Optional, NamedTuple
from errors import LineError, Position, get_whole_line, write_single_err
from string import ascii_letters, digits

@unique
class TokenType(Enum):
    Identifier = auto()
    Integer = auto()
    EOF = auto()
    Plus = auto()
    Minus = auto()
    Asterisk = auto()
    Slash = auto()
    LeftParen = auto()
    RightParen = auto()
    LeftBrace = auto()
    RightBrace = auto()
    Equals = auto()
    Semicolon = auto()
    Comma = auto()
    Colon = auto()

    Kw_Imp = auto()
    Kw_Fun = auto()

    Whitespace = auto()

class Token(NamedTuple):
    type: TokenType
    content: Optional[str]
    position: Position
    source: str

class LexError(NamedTuple):
    message: str
    position: Position

class Lexer:
    def __init__(self, input: str, source: str):
        self.input = input
        self.source = source
        self.index = 0
        self.tokens: list[Token] = []
        self.errors: list[LexError] = []

        self.row = 1
        self.col = 1

        self.recognized_chars: dict[str, TokenType] = {
            "+": TokenType.Plus,
            "-": TokenType.Minus,
            "*": TokenType.Asterisk,
            "/": TokenType.Slash,
            "(": TokenType.LeftParen,
            ")": TokenType.RightParen,
            "=": TokenType.Equals,
            ";": TokenType.Semicolon,
            "{": TokenType.LeftBrace,
            "}": TokenType.RightBrace,
            ",": TokenType.Comma,
            ":": TokenType.Colon
        }

        self.recognized_keywords = {
            "imp": TokenType.Kw_Imp,
            "fun": TokenType.Kw_Fun
        }

    def lex(self) -> 'list[Token]':
        while self.index < len(self.input):
            peeked = self.peek()

            if str.isalpha(peeked):               # identifier
                self.__lex_identifier()
            elif str.isdigit(peeked):             # integer
                self.__lex_integer()
            elif peeked == "\n" or peeked == " ": # whitespace
                self.__lex_whitespace()
            else:                                 # other
                pos = Position(self.index, self.row, self.col, self.row, self.col + 1)

                if peeked not in self.recognized_chars:
                    self.push_err(LexError(f"Unrecognized character: '{peeked}'", pos))
                else:
                    self.push(Token(self.recognized_chars[peeked], peeked, pos, self.source))

                self.index += 1
                self.col += 1
                
        self.tokens.append(Token(TokenType.EOF, None, Position(self.index, self.row, self.col, self.row, self.col), self.source))
        return self.tokens

    def __lex_integer(self):
        length = 0
        
        while self.index < len(self.input):
            peeked = self.peek(length)

            if peeked is not None and peeked in digits:
                length += 1
            else:
                break

        out = Token(TokenType.Identifier, self.input[self.index : self.index + length], 
            Position(self.index, self.row, self.col, self.row, self.col + length), self.source)

        self.push(out)

        self.col += length
        self.index += length

    def __lex_identifier(self):
        length = 0

        while self.index < len(self.input):
            peeked = self.peek(length)
            if peeked is not None and peeked in ascii_letters or length > 0 and peeked in digits:
                length += 1
            else:
                break
        
        string = self.input[self.index : self.index + length]
        type = self.recognized_keywords[string] if string in self.recognized_keywords else TokenType.Identifier

        out = Token(type, string, 
            Position(self.index, self.row, self.col, self.row, self.col + length), self.source)

        self.push(out)

        self.col += length
        self.index += length        

    def __lex_whitespace(self):
        length = 0
        new_row = self.row
        new_col = self.col

        while self.index < len(self.input):
            peeked = self.peek(length)
            if peeked is not None and peeked == "\n" or peeked == " ":
                if peeked == "\n":
                    new_row += 1
                    new_col = 0
                
                new_col += 1
                length += 1
            else:
                break

        out = Token(TokenType.Whitespace, self.input[self.index : self.index + length], 
            Position(self.index, self.row, self.col, self.row + new_row, self.col + new_col), self.source)

        self.col = new_col
        self.row = new_row
        self.index += length

        self.push(out)

    def peek(self, offset: int = 0) -> Optional[str]:
        if self.index + offset < len(self.input):
            return self.input[self.index + offset]
        else:
            return None

    def push(self, token: Token) -> None:
        self.tokens.append(token)

    def push_err(self, err: LexError) -> None:
        write_single_err(LineError(err.message, self.source, get_whole_line(self.input, err.position.index), err.position))
        self.errors.append(err)
        exit(1)