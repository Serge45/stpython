import pytest
from stpython.lexer import Token, TokenType
from stpython.parser import (
    Parser, evaluate, ASTNode, IntNode, FloatNode, StrNode, BinOpNode, UnaryOpNode, AssignOpNode, VarNode, Environment, BlockNode, IfNode
)


def make_token(ttype: TokenType, value: str | None) -> Token:
    return Token(line=1, column=1, ttype=ttype, value=value)

def parse_list(tokens_list: list[Token]) -> ASTNode:
    if not tokens_list or tokens_list[-1].ttype != TokenType.EOF:
        tokens_list = tokens_list + [make_token(TokenType.EOF, None)]
    parser = Parser(tokens_list)
    return parser.expr()

def test_ast_repr():
    """Verify the string representation of AST nodes."""
    tok_int = make_token(TokenType.INTEGER, "42")
    node_int = IntNode(tok_int)
    assert repr(node_int) == f"IntNode({tok_int})"

    tok_float = make_token(TokenType.FLOAT, "3.14")
    node_float = FloatNode(tok_float)
    assert repr(node_float) == f"FloatNode({tok_float})"

    tok_str = make_token(TokenType.STRING, "hello")
    node_str = StrNode(tok_str)
    assert repr(node_str) == f"StrNode({tok_str})"

    tok_plus = make_token(TokenType.PLUS, "+")
    node_bin = BinOpNode(tok_plus)
    node_bin.left = node_int
    node_bin.right = node_float
    assert repr(node_bin) == f"BinOpNode(l: IntNode({tok_int}) TokenType.PLUS, r: FloatNode({tok_float}))"

    tok_minus = make_token(TokenType.MINUS, "-")
    node_unary = UnaryOpNode(tok_minus)
    node_unary.val = tok_minus.value
    node_unary.expr = node_int
    assert repr(node_unary) == f"UnaryOpNode(op: TokenType.MINUS -)"


def test_parse_single_literal_int():
    tokens = [make_token(TokenType.INTEGER, "10")]
    ast = parse_list(tokens)
    assert isinstance(ast, IntNode)
    assert ast.token.value == "10"
    assert evaluate(ast) == 10

def test_parse_single_literal_float():
    tokens = [make_token(TokenType.FLOAT, "12.34")]
    ast = parse_list(tokens)
    assert isinstance(ast, FloatNode)
    assert ast.token.value == "12.34"
    assert evaluate(ast) == 12.34

def test_parse_single_literal_str():
    tokens = [make_token(TokenType.STRING, "test_string")]
    ast = parse_list(tokens)
    assert isinstance(ast, StrNode)
    assert ast.token.value == "test_string"
    assert evaluate(ast) == "test_string"

def test_parse_basic_addition():
    tokens = [
        make_token(TokenType.INTEGER, "5"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "3"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, IntNode)
    assert ast.left.token.value == "5"
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "3"
    assert evaluate(ast) == 8

def test_parse_basic_subtraction():
    tokens = [
        make_token(TokenType.INTEGER, "10"),
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.INTEGER, "4"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.MINUS
    assert evaluate(ast) == 6

def test_parse_basic_multiplication():
    tokens = [
        make_token(TokenType.INTEGER, "7"),
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "6"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.MULTIPLY
    assert evaluate(ast) == 42

def test_parse_basic_float_division():
    tokens = [
        make_token(TokenType.INTEGER, "7"),
        make_token(TokenType.FLOAT_DIVIDE, "/"),
        make_token(TokenType.INTEGER, "2"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.FLOAT_DIVIDE
    assert evaluate(ast) == 3.5

def test_parse_basic_int_division():
    tokens = [
        make_token(TokenType.INTEGER, "7"),
        make_token(TokenType.INT_DIVIDE, "//"),
        make_token(TokenType.INTEGER, "2"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.INT_DIVIDE
    assert evaluate(ast) == 3

def test_precedence_mul_before_add():
    # 2 + 3 * 4
    tokens = [
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "4"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, IntNode)
    assert ast.left.token.value == "2"
    assert isinstance(ast.right, BinOpNode)
    assert ast.right.op == TokenType.MULTIPLY
    assert evaluate(ast) == 14

def test_precedence_add_after_mul():
    # 2 * 3 + 4
    tokens = [
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "4"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, BinOpNode)
    assert ast.left.op == TokenType.MULTIPLY
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "4"
    assert evaluate(ast) == 10

def test_associativity_chained_addition():
    # 1 + 2 + 3
    # Left-associative: should parse as (1 + 2) + 3
    tokens = [
        make_token(TokenType.INTEGER, "1"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "3"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, BinOpNode)
    assert ast.left.op == TokenType.PLUS
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "3"
    assert evaluate(ast) == 6

def test_associativity_chained_subtraction():
    # 10 - 4 - 2
    # Left-associative: should parse as (10 - 4) - 2
    tokens = [
        make_token(TokenType.INTEGER, "10"),
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.INTEGER, "4"),
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.INTEGER, "2"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.MINUS
    assert isinstance(ast.left, BinOpNode)
    assert ast.left.op == TokenType.MINUS
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "2"
    assert evaluate(ast) == 4

def test_parentheses():
    # (1 + 2) * 3
    tokens = [
        make_token(TokenType.LEFT_PAREN, "("),
        make_token(TokenType.INTEGER, "1"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.RIGHT_PAREN, ")"),
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "3"),
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.MULTIPLY
    assert isinstance(ast.left, BinOpNode)
    assert ast.left.op == TokenType.PLUS
    assert isinstance(ast.right, IntNode)
    assert evaluate(ast) == 9

def test_unexpected_token_error():
    # E.g. "* 1" where an expression expects a term, but starts with "*"
    tokens = [
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "1")
    ]
    with pytest.raises(ValueError) as exc_info:
        parse_list(tokens)
    assert "Unexpected token" in str(exc_info.value)

def test_lexer_parser_integration():
    """Verify integration between Lexer and Parser for basic expressions."""
    from stpython.lexer import parse as lex_parse
    
    # "1 + 2"
    tokens = lex_parse("1 + 2")
    ast = parse_list(tokens)
    assert evaluate(ast) == 3

    # "(5 - 2) * 3"
    tokens = lex_parse("(5 - 2) * 3")
    ast = parse_list(tokens)
    assert evaluate(ast) == 9

def test_unmatched_parentheses():
    # (1 + 2
    tokens = [
        make_token(TokenType.LEFT_PAREN, "("),
        make_token(TokenType.INTEGER, "1"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "2"),
    ]
    with pytest.raises(ValueError) as exc_info:
        parse_list(tokens)
    assert "Expected ')'" in str(exc_info.value)

def test_unary_operators():
    # Test unary plus: +5
    tokens = [
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "5")
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.expr, IntNode)
    assert ast.expr.token.value == "5"
    assert evaluate(ast) == 5

    # Test unary minus: -3.14
    tokens = [
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.FLOAT, "3.14")
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.MINUS
    assert isinstance(ast.expr, FloatNode)
    assert ast.expr.token.value == "3.14"
    assert evaluate(ast) == -3.14

    # Test nested unary minus: --2
    tokens = [
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.INTEGER, "2")
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.MINUS
    assert isinstance(ast.expr, UnaryOpNode)
    assert ast.expr.op == TokenType.MINUS
    assert isinstance(ast.expr.expr, IntNode)
    assert evaluate(ast) == 2

    # Test unary minus with parentheses: -(5 + 3)
    tokens = [
        make_token(TokenType.MINUS, "-"),
        make_token(TokenType.LEFT_PAREN, "("),
        make_token(TokenType.INTEGER, "5"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.RIGHT_PAREN, ")")
    ]
    ast = parse_list(tokens)
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.MINUS
    assert isinstance(ast.expr, BinOpNode)
    assert evaluate(ast) == -8

    # Integration test with lexer for complex unary operator usage
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("- (5 + -3)")
    ast = parse_list(tokens)
    assert evaluate(ast) == -2


def parse_stmt_list(tokens_list: list[Token]) -> ASTNode:
    if not tokens_list or tokens_list[-1].ttype != TokenType.EOF:
        tokens_list = tokens_list + [make_token(TokenType.EOF, None)]
    parser = Parser(tokens_list)
    return parser.stmt()


def test_parse_assignment_basic():
    """Verify parsing of a basic assignment like x = 42."""
    tokens = [
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "42"),
    ]
    ast = parse_stmt_list(tokens)
    
    assert isinstance(ast, AssignOpNode)
    assert ast.op == TokenType.ASSIGN
    assert isinstance(ast.left, VarNode)
    assert ast.left.token.value == "x"
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "42"


def test_parse_assignment_complex_rhs():
    """Verify parsing of an assignment with a complex expression on the RHS."""
    tokens = [
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.PLUS, "+"),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.MULTIPLY, "*"),
        make_token(TokenType.INTEGER, "4"),
    ]
    ast = parse_stmt_list(tokens)
    
    assert isinstance(ast, AssignOpNode)
    assert ast.op == TokenType.ASSIGN
    assert isinstance(ast.left, VarNode)
    assert ast.left.token.value == "y"
    
    # RHS should be 2 + 3 * 4
    assert isinstance(ast.right, BinOpNode)
    assert ast.right.op == TokenType.PLUS
    assert evaluate(ast.right) == 14


def test_lexer_parser_assignment_integration():
    """Verify integration between Lexer and Parser for assignment statements."""
    from stpython.lexer import parse as lex_parse
    
    tokens = lex_parse("result = 12 + 5")
    ast = parse_stmt_list(tokens)
    
    assert isinstance(ast, AssignOpNode)
    assert ast.op == TokenType.ASSIGN
    assert isinstance(ast.left, VarNode)
    assert ast.left.token.value == "result"
    
    assert isinstance(ast.right, BinOpNode)
    assert ast.right.op == TokenType.PLUS
    assert evaluate(ast.right) == 17


def test_parse_name_in_expression():
    """Verify parsing a variable name inside an expression succeeds with VarNode."""
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("x + 1")
    ast = parse_stmt_list(tokens)
    
    assert isinstance(ast, BinOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, VarNode)
    assert ast.left.token.value == "x"
    assert isinstance(ast.right, IntNode)
    assert ast.right.token.value == "1"


def test_parse_assignment_rhs_name():
    """Verify that using a name on the RHS of assignment succeeds with VarNode."""
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("y = x")
    ast = parse_stmt_list(tokens)
    
    assert isinstance(ast, AssignOpNode)
    assert ast.op == TokenType.ASSIGN
    assert isinstance(ast.left, VarNode)
    assert ast.left.token.value == "y"
    
    assert isinstance(ast.right, VarNode)
    assert ast.right.token.value == "x"
    assert evaluate(ast) == "x"


def test_parse_single_name_no_eof_peek():
    """Verify that parsing a single NAME token with no subsequent token succeeds without crashing."""
    tokens = [make_token(TokenType.NAME, "x")]
    ast = parse_stmt_list(tokens)
    assert isinstance(ast, VarNode)
    assert ast.token.value == "x"


def test_environment_basic():
    """Verify that Environment stores and retrieves values correctly."""
    env = Environment()
    env["x"] = 42
    assert env["x"] == 42
    
    # Test setting and getting string and float
    env["pi"] = 3.14
    env["name"] = "test"
    assert env["pi"] == 3.14
    assert env["name"] == "test"


def test_evaluate_var_node_with_env():
    """Verify evaluating a VarNode with an environment returns its value."""
    env = Environment()
    env["x"] = 100
    node = VarNode(make_token(TokenType.NAME, "x"))
    assert evaluate(node, env) == 100


def test_evaluate_assignment_with_env():
    """Verify evaluating an assignment updates the environment and returns the value."""
    env = Environment()
    tokens = [
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "42"),
    ]
    ast = parse_stmt_list(tokens)
    res = evaluate(ast, env)
    assert res == 42
    assert env["x"] == 42


def test_evaluate_bin_op_with_env_propagation():
    """Verify that variables can be used in binary operations during evaluation."""
    env = Environment()
    env["x"] = 5
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("x + 1")
    ast = parse_stmt_list(tokens)
    assert evaluate(ast, env) == 6


def test_evaluate_assignment_rhs_var_with_env_propagation():
    """Verify that assigning a variable to another variable evaluates correctly using the env."""
    env = Environment()
    env["x"] = 42
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("y = x")
    ast = parse_stmt_list(tokens)
    
    res = evaluate(ast, env)
    assert res == 42
    assert env["y"] == 42


def test_environment_undefined_variable_raises_name_error():
    """Verify that referencing an undefined variable in the environment raises a NameError."""
    env = Environment()
    node = VarNode(make_token(TokenType.NAME, "a"))
    with pytest.raises(NameError) as exc_info:
        evaluate(node, env)
    assert "name a is not defined" in str(exc_info.value)


def test_parse_if_statement_basic():
    """Verify parsing of a basic 'if' statement without 'else'."""
    # Source:
    # if x:
    #   y = 2
    tokens = [
        make_token(TokenType.IF, "if"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.COLON, ":"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.stmt()
    
    assert isinstance(ast, IfNode)
    assert isinstance(ast.condition, VarNode)
    assert ast.condition.token.value == "x"
    
    assert isinstance(ast.then_branch, BlockNode)
    assert len(ast.then_branch.statements) == 1
    stmt = ast.then_branch.statements[0]
    assert isinstance(stmt, AssignOpNode)
    assert stmt.left.token.value == "y"
    assert stmt.right.token.value == "2"
    assert ast.else_branch is None


def test_parse_if_else_statement():
    """Verify parsing of an 'if' statement with an 'else' block."""
    # Source:
    # if x:
    #   y = 2
    # else:
    #   y = 3
    tokens = [
        make_token(TokenType.IF, "if"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.COLON, ":"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.ELSE, "else"),
        make_token(TokenType.COLON, ":"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.stmt()
    
    assert isinstance(ast, IfNode)
    assert isinstance(ast.condition, VarNode)
    assert ast.condition.token.value == "x"
    
    assert isinstance(ast.then_branch, BlockNode)
    assert len(ast.then_branch.statements) == 1
    assert ast.then_branch.statements[0].right.token.value == "2"
    
    assert isinstance(ast.else_branch, BlockNode)
    assert len(ast.else_branch.statements) == 1
    assert ast.else_branch.statements[0].right.token.value == "3"


def test_evaluate_if_then_branch():
    """Verify that evaluate executes the 'then' branch when condition is truthy (non-zero)."""
    env = Environment()
    env["x"] = 1
    
    # AST for:
    # if x:
    #   y = 2
    # else:
    #   y = 3
    
    cond = VarNode(make_token(TokenType.NAME, "x"))
    
    then_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    then_stmt.left = VarNode(make_token(TokenType.NAME, "y"))
    then_stmt.right = IntNode(make_token(TokenType.INTEGER, "2"))
    then_block = BlockNode(make_token(TokenType.INDENT, "  "))
    then_block.statements = [then_stmt]
    
    else_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    else_stmt.left = VarNode(make_token(TokenType.NAME, "y"))
    else_stmt.right = IntNode(make_token(TokenType.INTEGER, "3"))
    else_block = BlockNode(make_token(TokenType.INDENT, "  "))
    else_block.statements = [else_stmt]
    
    if_node = IfNode(make_token(TokenType.IF, "if"))
    if_node.condition = cond
    if_node.then_branch = then_block
    if_node.else_branch = else_block
    
    evaluate(if_node, env)
    assert env["y"] == 2


def test_evaluate_if_else_branch():
    """Verify that evaluate executes the 'else' branch when condition is falsy (zero)."""
    env = Environment()
    env["x"] = 0
    
    # Same AST as above
    cond = VarNode(make_token(TokenType.NAME, "x"))
    
    then_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    then_stmt.left = VarNode(make_token(TokenType.NAME, "y"))
    then_stmt.right = IntNode(make_token(TokenType.INTEGER, "2"))
    then_block = BlockNode(make_token(TokenType.INDENT, "  "))
    then_block.statements = [then_stmt]
    
    else_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    else_stmt.left = VarNode(make_token(TokenType.NAME, "y"))
    else_stmt.right = IntNode(make_token(TokenType.INTEGER, "3"))
    else_block = BlockNode(make_token(TokenType.INDENT, "  "))
    else_block.statements = [else_stmt]
    
    if_node = IfNode(make_token(TokenType.IF, "if"))
    if_node.condition = cond
    if_node.then_branch = then_block
    if_node.else_branch = else_block
    
    evaluate(if_node, env)
    assert env["y"] == 3


def test_evaluate_if_no_else_falsy_condition():
    """Verify that evaluate handles IfNode without else branch and falsy condition safely (returning None)."""
    env = Environment()
    env["x"] = 0
    
    cond = VarNode(make_token(TokenType.NAME, "x"))
    then_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    then_stmt.left = VarNode(make_token(TokenType.NAME, "y"))
    then_stmt.right = IntNode(make_token(TokenType.INTEGER, "2"))
    then_block = BlockNode(make_token(TokenType.INDENT, "  "))
    then_block.statements = [then_stmt]
    
    if_node = IfNode(make_token(TokenType.IF, "if"))
    if_node.condition = cond
    if_node.then_branch = then_block
    if_node.else_branch = None
    
    res = evaluate(if_node, env)
    assert res is None


def test_parser_missing_colon_attribute_error():
    """Verify that a missing colon raises a SyntaxError, not an AttributeError."""
    tokens = [
        make_token(TokenType.IF, "if"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(SyntaxError):
        parser.stmt()


def test_parser_missing_colon_else_syntax_error():
    """Verify that a missing colon after 'else' raises a SyntaxError, not an AttributeError."""
    tokens = [
        make_token(TokenType.IF, "if"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.COLON, ":"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.ELSE, "else"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "3"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(SyntaxError):
        parser.stmt()


def test_evaluate_multiple_nested_unary_operators():
    """Verify that multiple nested unary minus operators like '3----2' are correctly parsed and evaluated to 5."""
    from stpython.lexer import parse as lex_parse
    tokens = lex_parse("3----2")
    parser = Parser(tokens)
    ast = parser.expr()
    assert evaluate(ast) == 5


def test_parse_while_statement():
    """Verify parsing of a basic while loop."""
    from stpython.parser import WhileNode
    from stpython.lexer import TokenType
    tokens = [
        make_token(TokenType.WHILE, "while"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.COLON, ":"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.stmt()
    
    assert isinstance(ast, WhileNode)
    assert isinstance(ast.condition, VarNode)
    assert ast.condition.token.value == "x"
    assert isinstance(ast.body, BlockNode)
    assert len(ast.body.statements) == 1
    assert ast.body.statements[0].right.token.value == "2"


def test_parse_while_missing_colon():
    """Verify that a missing colon after 'while' condition raises a SyntaxError."""
    from stpython.lexer import TokenType
    tokens = [
        make_token(TokenType.WHILE, "while"),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.INDENT, "  "),
        make_token(TokenType.NAME, "y"),
        make_token(TokenType.ASSIGN, "="),
        make_token(TokenType.INTEGER, "2"),
        make_token(TokenType.NEWLINE, "\n"),
        make_token(TokenType.DEDENT, ""),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(SyntaxError):
        parser.stmt()


def test_evaluate_while_loop():
    """Verify that evaluate executes the while loop body until condition is falsy."""
    from stpython.parser import WhileNode
    from stpython.lexer import TokenType
    env = Environment()
    env["x"] = 3
    
    # AST for:
    # while x:
    #   x = x - 1
    cond = VarNode(make_token(TokenType.NAME, "x"))
    
    sub_expr = BinOpNode(make_token(TokenType.MINUS, "-"))
    sub_expr.left = VarNode(make_token(TokenType.NAME, "x"))
    sub_expr.right = IntNode(make_token(TokenType.INTEGER, "1"))
    
    body_stmt = AssignOpNode(make_token(TokenType.ASSIGN, "="))
    body_stmt.left = VarNode(make_token(TokenType.NAME, "x"))
    body_stmt.right = sub_expr
    
    body_block = BlockNode(make_token(TokenType.INDENT, "  "))
    body_block.statements = [body_stmt]
    
    while_node = WhileNode(make_token(TokenType.WHILE, "while"))
    while_node.condition = cond
    while_node.body = body_block
    
    evaluate(while_node, env)
    assert env["x"] == 0


def test_parse_print_statement():
    """Verify parsing of a print call statement."""
    from stpython.parser import CallNode
    tokens = [
        make_token(TokenType.NAME, "print"),
        make_token(TokenType.LEFT_PAREN, "("),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.RIGHT_PAREN, ")"),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.stmt()
    
    assert isinstance(ast, CallNode)
    assert ast.func_name == "print"
    assert len(ast.args) == 1
    assert isinstance(ast.args[0], VarNode)
    assert ast.args[0].token.value == "x"


def test_parse_print_missing_right_paren():
    """Verify that a missing right parenthesis in a print call raises an error."""
    tokens = [
        make_token(TokenType.NAME, "print"),
        make_token(TokenType.LEFT_PAREN, "("),
        make_token(TokenType.NAME, "x"),
        make_token(TokenType.EOF, None),
    ]
    parser = Parser(tokens)
    with pytest.raises(ValueError):
        parser.stmt()
        assert parser.cur_token.ttype == TokenType.EOF


def test_evaluate_print_statement(capsys):
    """Verify that evaluate prints the evaluated argument to stdout."""
    from stpython.parser import CallNode
    env = Environment()
    env["x"] = 42
    
    call_node = CallNode(make_token(TokenType.NAME, "print"))
    call_node.args = [VarNode(make_token(TokenType.NAME, "x"))]
    
    evaluate(call_node, env)
    
    captured = capsys.readouterr()
    assert captured.out == "42\n"


def test_integration_power_loop(capsys):
    """Verify parsing and evaluating a complete script with a while loop, variables, and print."""
    from stpython.lexer import parse as lex_parse
    
    code = """
val = 2
guess = 1
i = 5

while i:
    guess = guess * val
    i = i - 1
    print(guess)
"""
    tokens = lex_parse(code)
    parser = Parser(tokens)
    
    statements = []
    # Parse all statements until EOF
    while parser.cur_token.ttype != TokenType.EOF:
        statements.append(parser.stmt())
        
    env = Environment()
    for stmt in statements:
        evaluate(stmt, env)
        
    # Verify environment state
    assert env["val"] == 2
    assert env["guess"] == 32
    assert env["i"] == 0
    
    # Verify printed outputs
    captured = capsys.readouterr()
    assert captured.out == "2\n4\n8\n16\n32\n"
