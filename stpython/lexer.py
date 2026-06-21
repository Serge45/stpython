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
    INT_DIVIDE = auto()
    FLOAT_DIVIDE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
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

    def get_next_token(self) -> Token | None:
        while self.cursor < len(self.source):
            char = self.source[self.cursor]
            if char in ' \t':
                self.advance()
            elif char == '\n':
                self.advance(newline=True)
            else:
                break

        if self.cursor >= len(self.source):
            return Token(self.line, self.column, TokenType.EOF, None)

        char = self.source[self.cursor]
        
        if char == '+':
            token = Token(self.line, self.column, TokenType.PLUS, char)
            self.advance()
            return token
        elif char == '-':
            token = Token(self.line, self.column, TokenType.MINUS, char)
            self.advance()
            return token
        elif char == '(':
            token = Token(self.line, self.column, TokenType.LEFT_PAREN, char)
            self.advance()
            return token
        elif char == ')':
            token = Token(self.line, self.column, TokenType.RIGHT_PAREN, char)
            self.advance()
            return token
        elif char == '*':
            token = Token(self.line, self.column, TokenType.MULTIPLY, char)
            self.advance()
            return token
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
            return token
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
            token = Token(start_line, start_column, TokenType.NAME, "".join(chars))
            self.advance()
            return token
        elif char == '=':
            if self.peek() == '=':
                token = Token(self.line, self.column, TokenType.EQUAL, "==")
                #advance for second =
                self.advance()
            else:
                token = Token(self.line, self.column, TokenType.ASSIGN, char)
            self.advance()
            return token
        else:
            assert False, f"Unknown token {char} at {self.line}:{self.column}"

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
    