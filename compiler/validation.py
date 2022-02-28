from typing import NamedTuple
from errors import construct_line, write_single_err, LineError
from plast import Node, Program, FunctionDecl, Expression, FunctionCall, Identifier, \
    IntegerLiteral, Statement, BinaryOperation

class FunctionSymbol(NamedTuple):
    name: str
    location: str
    parameters: list['TypeSymbol']
    return_type: 'TypeSymbol'
    pure: bool

class TypeSymbol(NamedTuple):
    name: str
    location: str

Symbol = FunctionSymbol | TypeSymbol

class SymbolTable:
    symbols: dict['str', 'Symbol']

    def __init__(self):
        self.symbols = {}

    def exists_symbol(self, sym: Symbol) -> bool:
        return sym in self.symbols.values()

    def exists_name(self, name: str) -> bool:
        return name in self.symbols

    def add_symbol(self, sym: Symbol) -> bool:
        if self.exists_symbol(sym):
            return False

        self.symbols[sym.name] = sym
        return True

    def find_symbol(self, name: str) -> Symbol | None:
        if self.exists_name(name):
            return self.symbols[name]

        return False

def validate_ast(root: Program):
    symbols = __generate_default_symbols()

    # phase 1: symbol table generation
    for c in root.children:
        if (type(c) != FunctionDecl):
            pass
            
        params = []
        for p in c.parameters.params:
            name = p.type.token.content
            sym = symbols.find_symbol(name)

            if not sym or type(sym) != TypeSymbol:
                raise Exception(f"Unknown type {name}")

            params.append(p)

        ret = c.type.type.token.content
        retsym = symbols.find_symbol(ret)

        if not retsym or type(retsym) != TypeSymbol:
            raise Exception(f"Unknown type {ret}")

        fsym = FunctionSymbol(c.name.token.content, "sex", params, retsym, c.pure)
        if not symbols.add_symbol(fsym):
            raise Exception(f"fun {fsym.name} is already declared in scope")

    # phase 2: fun validation
    #  - return type must match value of expr
    #  - also ensure no identifiers are used before declaration
    for c in root.children:
        if (type(c) != FunctionDecl):
            pass

        ret_type = symbols.find_symbol(c.type.type.token.content)
        body_type = __get_expression_type(c.body, symbols, c.pure)

        if ret_type != body_type:
            val = construct_line(c.type.type.token)
            print(val)
            print("'" + val + "'")
            write_single_err(LineError(f"Function body return type {body_type.name} does not match declared return type {ret_type.name}",
                c.type.type.token.source, construct_line(c.type.type.token), c.type.type.token.position))
            raise Exception(f"Function body return type {body_type.name} does not match declared return type {ret_type.name}")

def __generate_default_symbols():
    st = SymbolTable()

    t_int = st.add_symbol(TypeSymbol("int", "builtin"))
    t_void = st.add_symbol(TypeSymbol("void", "builtin"))
    st.add_symbol(FunctionSymbol("print", "std.io", [t_int], t_void, False))

    return st

def __get_expression_type(expr: Node, symtable: SymbolTable, pure_only: bool): 
    t = type(expr)
    
    if t == Statement:
        return symtable.find_symbol("void")

    elif t == IntegerLiteral:
        return symtable.find_symbol("int")

    elif t == FunctionCall:
        fcall = symtable.find_symbol(expr.name.token.content)
        if not fcall or type(fcall) != FunctionSymbol:
            raise Exception(f"Could not find function '{expr.name.token.content}'")
        
        tsym = symtable.find_symbol(fcall.return_type)
        
        if pure_only and not fcall.pure:
            raise Exception(f"Can't invoke impure function '{expr.name.token.content}' from pure context")

        return tsym

    elif t == Identifier:
        ident = symtable.find_symbol(expr.value)
        if not ident:
            raise Exception(f"Use of undeclared symbol {expr.value}")

        return ident

    elif t == Expression:
        ty = None

        for c in expr.children:
            if type(c) == Statement:
                pass

            elif not ty:
                ty = __get_expression_type(c, symtable, pure_only)
            
            else:
                raise Exception("Unexpected statement after expression")

        return ty or symtable.find_symbol("void")

    elif t == BinaryOperation:
        left_type = __get_expression_type(expr.left, symtable, pure_only)
        right_type = __get_expression_type(expr.right, symtable, pure_only)
        if left_type == right_type:
            return left_type

    else:
        raise Exception(f"Cannot get type for AST node of type {t}")