from stpython.lexer import Token, TokenType
from typing import List

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

class UnaryOpNode(ASTNode):
    def __init__(self, token: Token):
        super().__init__(token)
        self.op = token.ttype
        self.val = token.value

    def __repr__(self):
        return f"UnaryOpNode(op: {self.op} {self.val})"

class Parser:
    def __init__(self, tokens: List[Token]):
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
        else:
            raise ValueError(f'Unexpected token {self.cur_token}')

def evaluate(node: ASTNode) -> int | float | str:
    if isinstance(node, IntNode):
        return int(node.token.value)
    elif isinstance(node, FloatNode):
        return float(node.token.value)
    elif isinstance(node, StrNode):
        return node.token.value
    elif isinstance(node, BinOpNode):
        left_val = evaluate(node.left)
        right_val = evaluate(node.right)
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
            return evaluate(node.expr)
        elif node.op == TokenType.MINUS:
            return -evaluate(node.expr)

if __name__ == '__main__':
    tokens = [
        Token(1, 1, TokenType.INTEGER, '1'),
        Token(1, 2, TokenType.PLUS, '+'),
        Token(1, 3, TokenType.INTEGER, '2'),
        Token(1, 4, TokenType.EOF, None)
    ]

    parser = Parser(tokens)
    ast = parser.expr()
    print(ast, ",", evaluate(ast))
