from typing import NamedTuple
from enum import Enum, auto

class ParseTreeNodeType(Enum):
    Program = auto(),
    BlockExpression = auto(),
    BlocklessExpression = auto(),
    Statement = auto(),
    PureFunction = auto(),
    ImpureFunction = auto(),
    ParamList = auto(),
    ArgumentList = auto(),
    FunctionCall = auto(),
    Term = auto(),
    Factor = auto(),
    Element = auto(),
    Token = auto(),
    Whitespace = auto()

class ParseTreeNode(NamedTuple):
    type: ParseTreeNodeType
    children: 'list[ParseTreeNode]'
    token: 'Token | None' = None


