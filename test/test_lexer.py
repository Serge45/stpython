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
        Token(line=1, column=2, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.PLUS, value="+"),
    ]

    tokens = collect_tokens("1\n\n\n=")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=2, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=4, column=1, ttype=TokenType.ASSIGN, value="="),
    ]

def test_unknown_character_assertion():
    """Verify that unknown characters raise an AssertionError."""
    with pytest.raises(AssertionError) as exc_info:
        collect_tokens("1@2")
    assert "Unknown token @" in str(exc_info.value)

    with pytest.raises(AssertionError) as exc_info:
        collect_tokens("@")
    assert "Unknown token @" in str(exc_info.value)

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


def test_name_tokens_basic():
    """Verify basic name tokenization (letters, starting underscores, alphanumeric combinations)."""
    # Single character names
    tokens = collect_tokens("a")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.NAME, value="a")]

    tokens = collect_tokens("_")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.NAME, value="_")]

    # Multi-character names
    tokens = collect_tokens("var1")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.NAME, value="var1")]

    tokens = collect_tokens("_abc123")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.NAME, value="_abc123")]

    # Names in expressions
    tokens = collect_tokens("x + y")
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.PLUS, value="+"),
        Token(line=1, column=5, ttype=TokenType.NAME, value="y"),
    ]


def test_name_tokens_with_underscores():
    """Verify name tokenization of names containing underscores in the middle or end."""
    tokens = collect_tokens("foo_bar")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.NAME, value="foo_bar")]


def test_float_tokens_basic():
    """Verify basic float tokenization."""
    tokens = collect_tokens("12.34")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.FLOAT, value="12.34")]


def test_float_tokens_multiple_decimals():
    """Verify that multiple decimal points in a float raise a TokenError."""
    with pytest.raises(TokenError):
        collect_tokens("1.2.3")


def test_basic_indent_dedent():
    """Verify single level of indentation and dedentation."""
    code = (
        "x = 1\n"
        "  y = 2\n"
        "z = 3"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=2, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=3, column=1, ttype=TokenType.NAME, value="z"),
        Token(line=3, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=3, column=5, ttype=TokenType.INTEGER, value="3"),
    ]


def test_eof_indent_cleanup():
    """Verify that any remaining indentation levels are cleaned up with DEDENT tokens at EOF."""
    code = (
        "x = 1\n"
        "  y = 2\n"
        "    z = 3"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=2, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.INDENT, value="    "),
        Token(line=3, column=5, ttype=TokenType.NAME, value="z"),
        Token(line=3, column=7, ttype=TokenType.ASSIGN, value="="),
        Token(line=3, column=9, ttype=TokenType.INTEGER, value="3"),
        Token(line=3, column=10, ttype=TokenType.DEDENT, value=""),
        Token(line=3, column=10, ttype=TokenType.DEDENT, value=""),
    ]


def test_nested_indent_dedent():
    """Verify nested indentation and multiple dedent tokens in sequence."""
    code = (
        "x = 1\n"
        "  y = 2\n"
        "    z = 3\n"
        "  w = 4\n"
        "a = 5"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=2, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.INDENT, value="    "),
        Token(line=3, column=5, ttype=TokenType.NAME, value="z"),
        Token(line=3, column=7, ttype=TokenType.ASSIGN, value="="),
        Token(line=3, column=9, ttype=TokenType.INTEGER, value="3"),
        Token(line=3, column=10, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=4, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=4, column=3, ttype=TokenType.NAME, value="w"),
        Token(line=4, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=4, column=7, ttype=TokenType.INTEGER, value="4"),
        Token(line=4, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=5, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=5, column=1, ttype=TokenType.NAME, value="a"),
        Token(line=5, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=5, column=5, ttype=TokenType.INTEGER, value="5"),
    ]


def test_whitespace_and_blank_lines():
    """Verify that completely empty lines or lines with only whitespace are ignored and do not trigger INDENT/DEDENT."""
    code = (
        "x = 1\n"
        "\n"
        "  \n"
        "  y = 2\n"
        "  \n"
        "z = 3"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=3, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=4, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=4, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=4, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=4, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=4, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=5, column=3, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=6, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=6, column=1, ttype=TokenType.NAME, value="z"),
        Token(line=6, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=6, column=5, ttype=TokenType.INTEGER, value="3"),
    ]


def test_mismatched_dedent_error():
    """Verify that a dedent to a non-existent indentation level raises a TokenError."""
    code = (
        "x = 1\n"
        "    y = 2\n"
        "  z = 3"
    )
    with pytest.raises(TokenError) as exc_info:
        collect_tokens(code)
    assert "indent" in str(exc_info.value).lower() or "dedent" in str(exc_info.value).lower()


def test_tab_indentation():
    """Verify that tabs can also be used for indentation, but mixing them with spaces is not allowed."""
    code = (
        "x = 1\n"
        "\ty = 2"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="\t"),
        Token(line=2, column=2, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=4, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=6, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=7, ttype=TokenType.DEDENT, value=""),
    ]


def test_mixed_indentation_error():
    """Verify that mixing spaces and tabs for indentation raises a TokenError."""
    code = (
        "x = 1\n"
        "  y = 2\n"
        "\t  z = 3"
    )
    with pytest.raises(TokenError):
        collect_tokens(code)


def test_multi_level_dedent():
    """Verify that dedenting multiple levels at once (e.g. from 4 spaces to 0 spaces) emits multiple DEDENT tokens."""
    code = (
        "x = 1\n"
        "  y = 2\n"
        "    z = 3\n"
        "a = 4"
    )
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=2, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.INDENT, value="    "),
        Token(line=3, column=5, ttype=TokenType.NAME, value="z"),
        Token(line=3, column=7, ttype=TokenType.ASSIGN, value="="),
        Token(line=3, column=9, ttype=TokenType.INTEGER, value="3"),
        Token(line=3, column=10, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=4, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=4, column=1, ttype=TokenType.DEDENT, value=""),
        Token(line=4, column=1, ttype=TokenType.NAME, value="a"),
        Token(line=4, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=4, column=5, ttype=TokenType.INTEGER, value="4"),
    ]


def test_trailing_spaces_eof_crash():
    """Verify that trailing spaces at the end of the file do not cause IndexError."""
    code = "x = 1\n  "
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
    ]


def test_trailing_spaces_eof_dedent_cleanup():
    """Verify that remaining indentation levels are cleaned up even with trailing whitespace at EOF."""
    code = "x = 1\n  y = 2\n  "
    tokens = collect_tokens(code)
    assert tokens == [
        Token(line=1, column=1, ttype=TokenType.NAME, value="x"),
        Token(line=1, column=3, ttype=TokenType.ASSIGN, value="="),
        Token(line=1, column=5, ttype=TokenType.INTEGER, value="1"),
        Token(line=1, column=6, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=2, column=1, ttype=TokenType.INDENT, value="  "),
        Token(line=2, column=3, ttype=TokenType.NAME, value="y"),
        Token(line=2, column=5, ttype=TokenType.ASSIGN, value="="),
        Token(line=2, column=7, ttype=TokenType.INTEGER, value="2"),
        Token(line=2, column=8, ttype=TokenType.NEWLINE, value="\n"),
        Token(line=3, column=1, ttype=TokenType.DEDENT, value=""),
    ]



def test_spaces_only_eof_crash():
    """Verify that a source file containing only spaces does not cause IndexError."""
    code = "  "
    tokens = collect_tokens(code)
    assert tokens == []


def test_leading_indentation_first_line():
    """Verify that leading indentation on the first line is not silently ignored."""
    code = "  x = 1"
    with pytest.raises(TokenError):
        collect_tokens(code)


def test_leading_indentation_after_blank_line():
    """Verify that leading indentation after a blank line is not silently ignored/allowed."""
    code = "\n  x = 1"
    with pytest.raises(TokenError):
        collect_tokens(code)


def test_lexer_colon_token():
    """Verify that a colon is tokenized as TokenType.COLON."""
    tokens = collect_tokens(":")
    assert tokens == [Token(line=1, column=1, ttype=TokenType.COLON, value=":")]


def test_lexer_if_else_keywords():
    """Verify that if and else are tokenized as IF and ELSE tokens instead of generic NAMEs."""
    tokens = collect_tokens("if x:\n  y = 2\nelse:\n  y = 3")
    
    assert len(tokens) >= 12
    assert tokens[0].ttype == TokenType.IF
    assert tokens[2].ttype == TokenType.COLON
    assert tokens[4].ttype == TokenType.INDENT
    assert tokens[9].ttype == TokenType.DEDENT
    assert tokens[10].ttype == TokenType.ELSE
    assert tokens[11].ttype == TokenType.COLON


def test_lexer_while_keyword():
    """Verify that 'while' is tokenized as a WHILE token."""
    tokens = collect_tokens("while x:")
    assert len(tokens) >= 3
    assert tokens[0].ttype == TokenType.WHILE
    assert tokens[1].ttype == TokenType.NAME
    assert tokens[2].ttype == TokenType.COLON


def test_lexer_all_binary_operators():
    """Verify that all Python binary operators are tokenized correctly."""
    # Test float division /
    tokens = collect_tokens("/")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.FLOAT_DIVIDE

    # Test integer division //
    tokens = collect_tokens("//")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.INT_DIVIDE

    # Test modulo %
    tokens = collect_tokens("%")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.MODULO

    # Test power **
    tokens = collect_tokens("**")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.EXPONENTIATION

    # Test bitwise AND &
    tokens = collect_tokens("&")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.BITWISE_AND

    # Test bitwise OR |
    tokens = collect_tokens("|")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.BITWISE_OR

    # Test bitwise XOR ^
    tokens = collect_tokens("^")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.BITWISE_XOR

    # Test bitwise left shift <<
    tokens = collect_tokens("<<")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.BITWISE_LEFTSHIFT

    # Test bitwise right shift >>
    tokens = collect_tokens(">>")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.BITWISE_RIGHTSHIFT

    # Test less than <
    tokens = collect_tokens("<")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.LESS_THAN

    # Test greater than >
    tokens = collect_tokens(">")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.GREATER_THAN

    # Test less than or equal to <=
    tokens = collect_tokens("<=")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.LESS_THAN_EQUAL

    # Test greater than or equal to >=
    tokens = collect_tokens(">=")
    assert len(tokens) == 1
    assert tokens[0].ttype == TokenType.GREATER_THAN_EQUAL
