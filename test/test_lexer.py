import pytest
from stpython.lexer import Lexer, Token, TokenType, TokenError

def collect_tokens(code: str) -> list[Token]:
    """Helper to collect all tokens from a Lexer instance."""
    lexer = Lexer(code)
    tokens = []
    while (tok := lexer.get_next_token()).ttype != TokenType.EOF:
        tokens.append(tok)
    return tokens

def test_empty_source():
    """Verify that an empty source returns no tokens."""
    tokens = collect_tokens("")
    assert tokens == []

def test_single_tokens():
    """Verify correct tokenization of individual characters."""
    # Plus token
    tokens = collect_tokens("+")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.PLUS, value="+")

    # Minus token
    tokens = collect_tokens("-")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.MINUS, value="-")

    # Multiply token
    tokens = collect_tokens("*")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.MULTIPLY, value="*")

    # Left paren token
    tokens = collect_tokens("(")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.LEFT_PAREN, value="(")

    # Right paren token
    tokens = collect_tokens(")")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.RIGHT_PAREN, value=")")

    # Assign token
    tokens = collect_tokens("=")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.ASSIGN, value="=")

    # Equal token
    tokens = collect_tokens("==")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.EQUAL, value="==")

    # Single digit integer token
    tokens = collect_tokens("5")
    assert len(tokens) == 1
    assert tokens[0] == Token(line=1, column=1, ttype=TokenType.INTEGER, value="5")

def test_all_digits():
    """Verify that all single digit characters from 0 to 9 are tokenized correctly."""
    for digit in "0123456789":
        tokens = collect_tokens(digit)
        assert len(tokens) == 1
        assert tokens[0] == Token(line=1, column=1, ttype=TokenType.INTEGER, value=digit)

def test_token_sequence():
    """Verify tokenization of a sequence of tokens without whitespace."""
    tokens = collect_tokens("1+1")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=2, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=3, ttype=TokenType.INTEGER, value="1"),
    ]

    tokens = collect_tokens("1=9")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=2, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=3, ttype=TokenType.INTEGER, value="9"),
    ]

def test_whitespace_skipping():
    """Verify that spaces and tabs are skipped and column count updates correctly."""
    tokens = collect_tokens("1 + 2")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=3, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="2"),
    ]

    tokens = collect_tokens("1\t+\t3")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=3, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="3"),
    ]

def test_newline_handling():
    """Verify that newlines are skipped, increment line count, and reset column count."""
    tokens = collect_tokens("1\n+")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=2, column=1, ttype=TokenType.PLUS, value="+"),
    ]

    tokens = collect_tokens("1\n\n\n=")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=4, column=1, ttype=TokenType.ASSIGN, value="="),
    ]

def test_unknown_character_assertion():
    """Verify that unknown characters raise an AssertionError."""
    with pytest.raises(AssertionError) as exc_info:
        collect_tokens("1%2")
    assert "Unknown token %" in str(exc_info.value)

    with pytest.raises(AssertionError) as exc_info:
        collect_tokens("x")
    assert "Unknown token x" in str(exc_info.value)

def test_trailing_whitespace():
    """Verify that trailing whitespace is handled correctly and does not cause an error."""
    tokens = collect_tokens("1+ ")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=2, ttype=TokenType.PLUS, value="+"),
    ]

def test_multi_digit_integer():
    """Verify that multi-digit integers are tokenized as a single token with correct starting column."""
    tokens = collect_tokens("123+45")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="123"),
        Token(line=1, column=4, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="45"),
    ]


def test_expression_with_new_tokens():
    """Verify tokenization of an expression containing parenthesis, multiplication, subtraction, and addition."""
    tokens = collect_tokens("(12 + 3) * 4 - 5")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.LEFT_PAREN, value="("),
        Token(line=1, column=2, ttype=TokenType.INTEGER, value="12"),
        Token(line=1, column=5, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=7, ttype=TokenType.INTEGER, value="3"),
        Token(line=1, column=8, ttype=TokenType.RIGHT_PAREN, value=")"),
        Token(line=1, column=10, ttype=TokenType.MULTIPLY, value="*"),
        Token(line=1, column=12, ttype=TokenType.INTEGER, value="4"),
        Token(line=1, column=14, ttype=TokenType.MINUS, value="-"),
        Token(line=1, column=16, ttype=TokenType.INTEGER, value="5"),
    ]


def test_leading_zeros_error():
    """Verify that integer literals with leading zeros raise a TokenError."""
    with pytest.raises(TokenError) as exc_info:
        collect_tokens("01")
    assert "Leading zeros in decimal integer literals are not permitted: 01" in str(exc_info.value)

    with pytest.raises(TokenError) as exc_info:
        collect_tokens("00")
    assert "Leading zeros in decimal integer literals are not permitted: 00" in str(exc_info.value)

    with pytest.raises(TokenError) as exc_info:
        collect_tokens("0123")
    assert "Leading zeros in decimal integer literals are not permitted: 0123" in str(exc_info.value)

    with pytest.raises(TokenError) as exc_info:
        collect_tokens("1 + 02")
    assert "Leading zeros in decimal integer literals are not permitted: 02" in str(exc_info.value)

