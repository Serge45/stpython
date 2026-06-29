from stpython.lexer import Token, TokenType
from typing import List, FrozenSet

BUILTIN_FUNCTIONS: FrozenSet[str] = frozenset({'print'})

class ASTNode:
    def __init__(self, token: Token):
        self.token = token

class IntNode(ASTNode):
    def __repr__(self):
        return f"IntNode({self.token})"

class FloatNode(ASTNode):
    def __repr__(self):
        return f"FloatNode({self.token})"

class StrNode(ASTNode):
    def __repr__(self):
        return f"StrNode({self.token})"

class BinOpNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.op = token.ttype
        self.left = None
        self.right = None

    def __repr__(self):
        return f"BinOpNode(l: {self.left} {self.op}, r: {self.right})"

class AssignOpNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.op = token.ttype
        self.left = None
        self.right = None

    def __repr__(self):
        return f"AssignOpNode(l: {self.left} {self.op}, r: {self.right})"

class VarNode(ASTNode):
    def __repr__(self):
        return f"VarNode({self.token.value})"

class UnaryOpNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.op = token.ttype
        self.val = token.value

    def __repr__(self):
        return f"UnaryOpNode(op: {self.op} {self.val})"

class BlockNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.statements: List[ASTNode] = []

    def __repr__(self):
        return f"BlockNode({self.statements})"

class IfNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.condition: ASTNode = None
        self.then_branch: BlockNode = None
        self.else_branch: BlockNode = None

    def __repr__(self):
        return f"IfNode(cond: {self.condition}, then: {self.then_branch}, else: {self.else_branch})"

class WhileNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.condition: ASTNode = None
        self.body: BlockNode = None

    def __repr__(self):
        return f"WhileNode(cond: {self.condition}, body: {self.body})"

class CallNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.func_name: str = self.token.value
        self.args: List[ASTNode] = []

    def __repr__(self):
        return f"CallNode(func_name: {self.func_name}, args: {self.args})"

class Parser:
    def __init__(self, tokens: List[Token]):
        if tokens and tokens[-1].ttype != TokenType.EOF:
            last_tok = tokens[-1]
            col = last_tok.column + len(str(last_tok.value or ''))
            tokens = list(tokens) + [Token(last_tok.line, col, TokenType.EOF, None)]
        elif not tokens:
            tokens = [Token(1, 1, TokenType.EOF, None)]
        self.tokens = tokens
        self.cursor = -1
        self.cur_token = self.advance()

    def peek(self) -> Token | None:
        if self.cursor + 1 >= len(self.tokens):
            return None
        return self.tokens[self.cursor + 1]

    def advance(self) -> Token | None:
        if self.cursor >= len(self.tokens):
            return None
        self.cursor += 1
        self.cur_token = self.tokens[self.cursor] if self.cursor < len(self.tokens) else None
        return self.cur_token

    def advance_until_nonnewline(self) -> Token:
        while self.cur_token.ttype == TokenType.NEWLINE:
            self.advance()
        return self.cur_token

    def block(self) -> BlockNode:
        self.advance_until_nonnewline()

        assert self.cur_token.ttype == TokenType.INDENT
        self.advance()
        node = BlockNode(self.cur_token)

        while self.cur_token.ttype != TokenType.DEDENT:
            node.statements.append(self.stmt())
            self.advance_until_nonnewline()

        assert self.cur_token.ttype == TokenType.DEDENT
        self.advance()
        return node

    def stmt(self) -> ASTNode:
        self.advance_until_nonnewline()

        if self.cur_token.ttype == TokenType.IF:
            node = IfNode(self.cur_token)
            self.advance()
            node.condition = self.expr()
            if self.cur_token.ttype != TokenType.COLON:
                raise SyntaxError(f"{self.cur_token.line}:{self.cur_token.column} Expected ':' after 'if' condition.")
            self.advance()
            node.then_branch = self.block()

            if self.cur_token.ttype == TokenType.ELSE:
                self.advance()
                if self.cur_token.ttype != TokenType.COLON:
                    raise SyntaxError(f"{self.cur_token.line}:{self.cur_token.column} Expected ':' after 'else' statement.")
                self.advance()
                node.else_branch = self.block()
            return node
        elif self.cur_token.ttype == TokenType.WHILE:
            node = WhileNode(self.cur_token)
            self.advance()
            node.condition = self.expr()
            if self.cur_token.ttype != TokenType.COLON:
                raise SyntaxError(f"{self.cur_token.line}:{self.cur_token.column} Expected ':' after 'while' condition.")
            self.advance()
            node.body = self.block()
            return node
        # for x = 1 pattern
        elif self.cur_token.ttype == TokenType.NAME and self.peek() is not None and self.peek().ttype == TokenType.ASSIGN:
            name = self.cur_token
            self.advance()
            assign = self.cur_token
            self.advance()
            node = AssignOpNode(assign)
            node.left = VarNode(name)
            node.right = self.expr()
            return node
        return self.expr()

    def expr(self) -> ASTNode:
        """
        term [+, -] term
        """
        left = self.term()
        while self.cur_token.ttype in (TokenType.PLUS, TokenType.MINUS):
            op = self.cur_token
            self.advance()
            right = self.term()
            node = BinOpNode(op)
            node.left = left
            node.right = right
            left = node
        return left

    def term(self) -> ASTNode:
        """
        handle factor [*, /, //] factor
        """
        left = self.factor()
        while self.cur_token.ttype in (TokenType.MULTIPLY, TokenType.INT_DIVIDE, TokenType.FLOAT_DIVIDE):
            op = self.cur_token
            self.advance()
            right = self.factor()
            node = BinOpNode(op)
            node.left = left
            node.right = right
            left = node
        return left

    def factor(self) -> ASTNode:
        if self.cur_token.ttype == TokenType.INTEGER:
            node = IntNode(self.cur_token)
            self.advance()
            return node
        elif self.cur_token.ttype == TokenType.FLOAT:
            node = FloatNode(self.cur_token)
            self.advance()
            return node
        elif self.cur_token.ttype == TokenType.STRING:
            node = StrNode(self.cur_token)
            self.advance()
            return node
        elif self.cur_token.ttype == TokenType.LEFT_PAREN:
            self.advance()
            node = self.expr()
            if self.cur_token is None or self.cur_token.ttype != TokenType.RIGHT_PAREN:
                raise ValueError("Expected ')'")
            self.advance()
            return node
        elif self.cur_token.ttype in (TokenType.PLUS, TokenType.MINUS):
            node = UnaryOpNode(self.cur_token)
            self.advance()
            node.expr = self.factor()
            return node
        elif self.cur_token.ttype == TokenType.NAME:
            if self.cur_token.value in BUILTIN_FUNCTIONS:
                node = CallNode(self.cur_token)
                self.advance()
                if self.cur_token.ttype != TokenType.LEFT_PAREN:
                    raise ValueError("Expected '('")
                self.advance()

                while self.cur_token.ttype != TokenType.RIGHT_PAREN:
                    node.args.append(self.expr())

                    if self.cur_token.ttype == TokenType.RIGHT_PAREN:
                        break
                    elif self.cur_token.ttype != TokenType.COMMA:
                        if self.peek() is None:
                            raise ValueError(f"{self.cur_token.line}:{self.cur_token.column} Expected ',' or ')' after '{node.func_name}' function call.")
                        elif self.peek().ttype != TokenType.RIGHT_PAREN:
                            raise ValueError(f"{self.cur_token.line}:{self.cur_token.column} Expected ',' or ')' after '{node.func_name}' function call.")
                    
                    self.advance()

                if self.cur_token is None or self.cur_token.ttype != TokenType.RIGHT_PAREN:
                    raise ValueError(f"{self.cur_token.line}:{self.cur_token.column} Expected ')' after '{node.func_name}' function call.")
                # skip )
                self.advance()
                return node
            else:
                node = VarNode(self.cur_token)
                self.advance()
                return node
        else:
            raise ValueError(f'Unexpected token {self.cur_token}')

class Environment:
    def __init__(self):
        self.values = {}
        self.builtins = {
            "print": print
        }

    def __getitem__(self, key: str) -> int | float | str:
        if key not in self.values:
            raise NameError(f'name {key} is not defined')
        return self.values[key]

    def __setitem__(self, key: str, value: int | float | str) -> None:
        self.values[key] = value

def evaluate(node: ASTNode, env: Environment = None) -> int | float | str:
    if isinstance(node, IntNode):
        return int(node.token.value)
    elif isinstance(node, FloatNode):
        return float(node.token.value)
    elif isinstance(node, StrNode):
        return node.token.value
    elif isinstance(node, BinOpNode):
        left_val = evaluate(node.left, env)
        right_val = evaluate(node.right, env)
        if node.op == TokenType.PLUS:
            return left_val + right_val
        elif node.op == TokenType.MINUS:
            return left_val - right_val
        elif node.op == TokenType.MULTIPLY:
            return left_val * right_val
        elif node.op == TokenType.INT_DIVIDE:
            return left_val // right_val
        elif node.op == TokenType.FLOAT_DIVIDE:
            return left_val / right_val
    elif isinstance(node, UnaryOpNode):
        if node.op == TokenType.PLUS:
            return evaluate(node.expr, env)
        elif node.op == TokenType.MINUS:
            return -evaluate(node.expr, env)
    elif isinstance(node, AssignOpNode):
        if env is None:
            return evaluate(node.right, env)
        env[node.left.token.value] = evaluate(node.right, env)
        return env[node.left.token.value]
    elif isinstance(node, VarNode):
        if env is None:
            return node.token.value
        return env[node.token.value]
    elif isinstance(node, BlockNode):
        last = None
        for statement in node.statements:
            last = evaluate(statement, env)
        return last
    elif isinstance(node, IfNode):
        ret = None
        if evaluate(node.condition, env):
            ret = evaluate(node.then_branch, env)
        elif node.else_branch is not None:
            ret = evaluate(node.else_branch, env)
        return ret
    elif isinstance(node, WhileNode):
        ret = None
        while evaluate(node.condition, env):
            ret = evaluate(node.body, env)
        return ret
    elif isinstance(node, CallNode):
        func = env.builtins.get(node.func_name, None)
        if func is None:
            raise NameError(f'name {node.func_name} is not defined')
        args = [evaluate(arg, env) for arg in node.args]
        return func(*args)
    else:
        raise ValueError(f'Unexpected node {node}')

if __name__ == '__main__':
    tokens = [
        Token(1, 1, TokenType.INTEGER, '1'),
        Token(1, 2, TokenType.PLUS, '+'),
        Token(1, 3, TokenType.INTEGER, '2'),
        Token(1, 4, TokenType.EOF, None)
    ]

    parser = Parser(tokens)
    ast = parser.stmt()
    print(ast, ",", evaluate(ast))
