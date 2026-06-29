# stpython: A Toy Python Lexer, Parser & Interpreter

`stpython` is an educational, hands-on implementation of a custom Python subset interpreter written from scratch in Python. It serves as a learning resource demonstrating the fundamental phases of interpreter construction: lexical analysis (tokenization), recursive-descent parsing (AST generation), and AST-based evaluation.

---

## 🏗️ Architecture Overview

The codebase is split into clean, modular components:

1. **Lexical Analyzer ([stpython/lexer.py](file:///home/serge45/stpython/stpython/lexer.py))**
   * Translates raw source code character-by-character into token streams.
   * Handles Python's indentation-sensitive block structure by managing an internal `indent_stack` to yield `INDENT` and `DEDENT` tokens.
   * Handles literals (integers, floats, strings) and key statements (`if`, `else`, `while`, `print`).

2. **Parser & Evaluator ([stpython/parser.py](file:///home/serge45/stpython/stpython/parser.py))**
   * Implements a hand-written recursive-descent parser that consumes token sequences and builds an Abstract Syntax Tree (AST) composed of strongly typed AST nodes.
   * Evaluates the parsed AST nodes recursively via `evaluate()` inside a stateful execution context (`Environment`).

3. **Test Suite ([test/](file:///home/serge45/stpython/test))**
   * Built on `pytest` for robust test coverage.
   * Includes comprehensive unit tests for lexical token correctness, expression parsing precedence, syntax error verification, and runtime evaluation.

---

## 🚀 Supported Syntax Features

Currently, `stpython` supports a basic educational subset of Python features:
* **Literal Types:** Integers (`42`), Floats (`3.14`), and Strings (`"hello"`)
* **Arithmetic Expressions:** Binary operations (`+`, `-`, `*`) and nested Unary operations (`---x`)
* **Variables:** Variable assignment (`x = 10`) and resolution
* **Control Flow:** 
  * Conditional `if`/`else` blocks
  * `while` loops (with truthy/falsy evaluation)
* **Built-in Functions:** Built-in `print()` call execution

---

## 🛠️ Getting Started

### 📋 Prerequisites
This project uses the modern, ultra-fast Python package and project manager [uv](https://github.com/astral-sh/uv).

### 🧪 Running Tests
To run the full test suite and verify parser/lexer correctness:
```bash
uv run pytest
```

### 💻 Executing Code Example
You can parse and evaluate scripts using the library API:

```python
from stpython.lexer import parse
from stpython.parser import Parser, evaluate, Environment, TokenType

# Input code script
code = """
val = 2
guess = 1
i = 5

while i:
    guess = guess * val
    i = i - 1
    print(guess)
"""

# 1. Lexical Analysis
tokens = parse(code)

# 2. Parsing into statements
parser = Parser(tokens)
statements = []
while parser.cur_token.ttype != TokenType.EOF:
    statements.append(parser.stmt())

# 3. Environment & AST Evaluation
env = Environment()
for stmt in statements:
    evaluate(stmt, env)
```

---

## 🎓 Educational Extensions & Challenges

As an educational project, here are some recommended features to implement next to expand the interpreter's capabilities:
* **Division Operators:** Add support for `/` (float division) and `//` (floor division).
* **Comparison Operators:** Add relational parsing (`<`, `>`, `<=`, `>=`, `==`, `!=`).
* **Source Comments:** Add support to strip out `#` comments in the lexer.
