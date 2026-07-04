from enum import unique
import dataclasses
from enum import Enum, auto
from typing import List, Any
from dataclasses import dataclass

class TokenError(Exception):
    pass

class TokenType(Enum):
    ASSIGN = auto()
    EQUAL = auto()
    NAME = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    EXPONENTIATION = auto()
    INT_DIVIDE = auto()
    FLOAT_DIVIDE = auto()
    LESS_THAN = auto()
    LESS_THAN_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_THAN_EQUAL = auto()
    MODULO = auto()
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    BITWISE_NOT = auto()
    BITWISE_LEFTSHIFT = auto()
    BITWISE_RIGHTSHIFT = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    COLON = auto()
    COMMA = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    EOF = auto()

@dataclass
class Token:
    line: int
    column: int
    ttype: TokenType
    value: Any

class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: List[Token] = []
        self.line: int = 1
        self.column: int = 1
        self.cursor: int = 0
        self.cur_token: Token | None = None
        self.indent_stack: List[str] = ['']
        self.pending_dedent: List = []
        self.has_content: bool = False

    def advance(self, newline=False) -> str | None:
        if self.cursor >= len(self.source):
            return None
            
        self.cursor += 1

        if newline:
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        if self.cursor >= len(self.source):
            return None
            
        return self.source[self.cursor]

    def peek(self) -> str | None:
        if self.cursor + 1 >= len(self.source):
            return None
        return self.source[self.cursor + 1]

    def handle_newline(self) -> Token | None:
        chars = []
        indent_col = self.column
        while self.cursor < len(self.source) and self.source[self.cursor] in ' \t':
            chars.append(self.source[self.cursor])
            self.advance()

        if self.cursor >= len(self.source):
            return None

        if self.source[self.cursor] == '\n':
            # consume all following empty lines
            while self.peek() == '\n':
                self.advance(newline=True)
            return None

        indent = ''.join(chars)
        last_indent = self.indent_stack[-1]

        if len(set(indent)) > 1:
            raise TokenError(f"Mixed spaces and tabs in indentation at {self.line}:{self.column}")

        if len(indent) > len(last_indent):
            if self.has_content is False and last_indent == '':
                raise TokenError(f"Unexpected indent at {self.line}:{self.column}")
            self.indent_stack.append(indent)
            return Token(self.line, indent_col, TokenType.INDENT, indent)
        elif len(indent) == len(last_indent):
            if indent == last_indent:
                return None
            raise TokenError(f"Unexpected indent at {self.line}:{self.column}")
        else:
            while len(self.indent_stack[-1]) > len(indent):
                self.pending_dedent.append(Token(self.line, indent_col, TokenType.DEDENT, ''))
                self.indent_stack.pop()
            if self.indent_stack[-1] != indent:
                raise TokenError(f"Unexpected indent at {self.line}:{self.column}")
            return None

    def get_next_token(self) -> Token | None:
        if self.pending_dedent:
            self.cur_token = self.pending_dedent.pop()
            return self.cur_token

        if self.cursor >= len(self.source):
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                self.cur_token = Token(self.line, self.column, TokenType.DEDENT, '')
            else:
                self.cur_token = Token(self.line, self.column, TokenType.EOF, None)
            return self.cur_token

        if (self.cur_token is not None and self.cur_token.ttype == TokenType.NEWLINE) or self.column == 1:
            token = self.handle_newline()
            if token is not None:
                self.cur_token = token
                return token
            elif self.pending_dedent:
                self.cur_token = self.pending_dedent.pop()
                return self.cur_token

        # consume non-leading spaces and tabs
        while self.cursor < len(self.source) and self.source[self.cursor] in ' \t':
            self.advance()

        # handle trailing spaces, only one newline at the end of the file and EOF
        if self.cursor >= len(self.source):
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                self.cur_token = Token(self.line, 1, TokenType.DEDENT, '')
            else:
                self.cur_token = Token(self.line, self.column, TokenType.EOF, None)
            return self.cur_token

        char = self.source[self.cursor]

        if char == '\n':
            token = Token(self.line, self.column, TokenType.NEWLINE, char)
            self.advance(newline=True)
        elif char == '+':
            token = Token(self.line, self.column, TokenType.PLUS, char)
            self.advance()
        elif char == '-':
            token = Token(self.line, self.column, TokenType.MINUS, char)
            self.advance()
        elif char == '(':
            token = Token(self.line, self.column, TokenType.LEFT_PAREN, char)
            self.advance()
        elif char == ')':
            token = Token(self.line, self.column, TokenType.RIGHT_PAREN, char)
            self.advance()
        elif char == '*':
            next_char = self.peek()
            if next_char == '*':
                token = Token(self.line, self.column, TokenType.EXPONENTIATION, '**')
                self.advance()
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.MULTIPLY, char)
                self.advance()
        elif char == '/':
            next_char = self.peek()
            if next_char == '/':
                token = Token(self.line, self.column, TokenType.INT_DIVIDE, '//')
                self.advance()
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.FLOAT_DIVIDE, '/')
                self.advance()
        elif char == '%':
            token = Token(self.line, self.column, TokenType.MODULO, '%')
            self.advance()
        elif char == '|':
            token = Token(self.line, self.column, TokenType.BITWISE_OR, '|')
            self.advance()
        elif char == '&':
            token = Token(self.line, self.column, TokenType.BITWISE_AND, '&')
            self.advance()
        elif char == '^':
            token = Token(self.line, self.column, TokenType.BITWISE_XOR, '^')
            self.advance()
        elif char == '<':
            next_char = self.peek()
            if next_char == '<':
                token = Token(self.line, self.column, TokenType.BITWISE_LEFTSHIFT, '<<')
                self.advance()
                self.advance()
            elif next_char == '=':
                token = Token(self.line, self.column, TokenType.LESS_THAN_EQUAL, '<=')
                self.advance()
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.LESS_THAN, '<')
                self.advance()
        elif char == '>':
            next_char = self.peek()
            if next_char == '>':
                token = Token(self.line, self.column, TokenType.BITWISE_RIGHTSHIFT, '>>')
                self.advance()
                self.advance()
            elif next_char == '=':
                token = Token(self.line, self.column, TokenType.GREATER_THAN_EQUAL, '>=')
                self.advance()
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.GREATER_THAN, '>')
                self.advance()
        elif char == ',':
            token = Token(self.line, self.column, TokenType.COMMA, char)
            self.advance()
        elif char in '1234567890':
            start_line = self.line
            start_column = self.column
            chars = [char]
            while next_char := self.peek():
                if next_char in '1234567890.':
                    self.advance()
                    chars.append(next_char)
                else:
                    break

            if len(chars) > 1:
                if chars[0] == '0':
                    raise TokenError(f"Leading zeros in decimal integer literals are not permitted: {''.join(chars)}")

                num_dots = len([i for i in chars if i == '.'])
                if num_dots == 1:
                    token = Token(start_line, start_column, TokenType.FLOAT, "".join(chars))
                    self.advance()
                    return token
                elif num_dots > 1:
                    raise TokenError(f"Multiple decimal points in floating point literal: {''.join(chars)}")
            
            token = Token(start_line, start_column, TokenType.INTEGER, "".join(chars))
            self.advance()
        elif char.isalpha() or char == '_':
            start_line = self.line
            start_column = self.column
            chars = [char]
            while next_char := self.peek():
                if next_char.isalnum() or next_char == '_':
                    self.advance()
                    chars.append(next_char)
                else:
                    break

            name = "".join(chars)

            if name == "if":
                token = Token(start_line, start_column, TokenType.IF, name)
            elif name == "else":
                token = Token(start_line, start_column, TokenType.ELSE, name)
            elif name == "while":
                token = Token(start_line, start_column, TokenType.WHILE, name)
            else:
                token = Token(start_line, start_column, TokenType.NAME, name)
            self.advance()
        elif char == '=':
            if self.peek() == '=':
                token = Token(self.line, self.column, TokenType.EQUAL, "==")
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.ASSIGN, char)
            self.advance()
        elif char == ':':
            token = Token(self.line, self.column, TokenType.COLON, char)
            self.advance()
        else:
            assert False, f"Unknown token {char} at {self.line}:{self.column}"

        self.cur_token = token

        if self.has_content is False and token.ttype not in (TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE,):
            self.has_content = True

        # consume trailing spaces and tabs
        if self.cur_token and self.cur_token.ttype != TokenType.NEWLINE:
            while self.cursor < len(self.source) and self.source[self.cursor] in ' \t':
                self.advance()
        return token

def parse(code: str) -> List[Token]:
    lexer = Lexer(code)
    tokens = []
    while (tok := lexer.get_next_token()).ttype != TokenType.EOF:
        tokens.append(tok)
    return tokens
    
if __name__ == '__main__':
    print(parse("1+2"))
    print(parse("123+456"))
    print(parse("abc = 1"))
    