import re
Data Structure for AST:


class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type  # 'operator' for AND/OR, 'operand' for conditions
        self.value = value  # e.g., 'age > 30' for operand nodes
        self.left = left  # left child node
        self.right = right  # right child node

    def __repr__(self):
        return f"Node({self.type}, {self.value}, {self.left}, {self.right})"


CREATE TABLE rules(
    id SERIAL PRIMARY KEY,
    rule_string TEXT NOT NULL,
    ast_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)


# API Design:

# 1. create_rule(rule_string)


def create_rule(rule_string):
    tokens = tokenize_rule(rule_string)
    ast = parse_tokens_to_ast(tokens)
    return ast


def tokenize_rule(rule_string):
    # A simple tokenizer to break the rule string into components
    token_pattern = r'(\\band\\b|\\bor\\b|\\(|\\)|>|=|<|\\w+)'
    tokens = re.findall(token_pattern, rule_string.lower())
    return tokens


def parse_tokens_to_ast(tokens):
    # Recursive parsing of tokens into an AST structure
    stack = []
    for token in tokens:
        if token == '(':
            stack.append(token)
        elif token == ')':
            expr = []
            while stack and stack[-1] != '(':
                expr.append(stack.pop())
            stack.pop()  # Remove '('
            stack.append(build_ast(expr[::-1]))
        else:
            stack.append(token)
    return stack[0]


def build_ast(expr):
    # Recursively build the AST from token expressions
    if len(expr) == 1:
        return Node('operand', expr[0])
    if 'and' in expr:
        idx = expr.index('and')
        return Node('operator', 'and', build_ast(expr[:idx]), build_ast(expr[idx + 1:]))
    if 'or' in expr:
        idx = expr.index('or')
        return Node('operator', 'or', build_ast(expr[:idx]), build_ast(expr[idx + 1:]))


2. combine_rules(rules)
This function merges multiple rules into one AST while optimizing for efficiency:


def combine_rules(rule_asts):
    if len(rule_asts) == 1:
        return rule_asts[0]

    combined_ast = rule_asts[0]
    for rule_ast in rule_asts[1:]:
        combined_ast = Node('operator', 'and', combined_ast, rule_ast)
    return combined_ast


3. evaluate_rule(ast, data)
Evaluates a given AST against a dictionary of user attributes:


def evaluate_rule(ast, data):
    if ast.type == 'operand':
        return eval_operand(ast.value, data)
    elif ast.type == 'operator':
        left_eval = evaluate_rule(ast.left, data)
        right_eval = evaluate_rule(ast.right, data)
        if ast.value == 'and':
            return left_eval and right_eval
        elif ast.value == 'or':
            return left_eval or right_eval


def eval_operand(operand, data):
    # Parse condition like "age > 30"
    field, op, value = re.split(r'(>|<|=)', operand)
    field = field.strip()
    value = value.strip().strip("'")

    # Handle comparison
    if op == '>' and data[field] > int(value):
        return True
    elif op == '<' and data[field] < int(value):
        return True
    elif op == '=' and str(data[field]) == value:
        return True
    return False


# Test Cases:

# 1. Create Rules:
   #rule1 = create_rule("((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)")
  # print(rule1)


# 2. Combine Rules:
   #combined_rule = combine_rules([rule1, rule2])
  # print(combined_rule)


# 3. Evaluate Rules:
   #data = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}
  # result = evaluate_rule(combined_rule, data)
  # print(result)  # Should return True or False based on the evaluation
