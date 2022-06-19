import argparse
import os
import re
import ast


def analyze(filepath):
    with open(filepath, 'r') as file, open(filepath, 'r') as py_file:
        lines = file.readlines()
        func_mistakes = check_func_mistakes(py_file)

        empty_lines = 0
        for num, line in enumerate(lines, start=1):
            if empty_lines == 3:
                print_error(filepath, num, 'S006', 'More than two blank lines preceding a code line')
                empty_lines = 0
            if not line.strip():
                empty_lines += 1
            else:
                empty_lines = 0
                check_length(num, line, filepath)
                check_indentation(num, line, filepath)
                check_semicolon(num, line, filepath)
                check_comments(num, line, filepath)
                check_todo(num, line, filepath)
                check_construction_spaces(num, line, filepath)
                check_class_name(num, line, filepath)
                check_func_name(num, line, filepath)

            if num in [v for v in func_mistakes['S010']]:
                print_error(filepath, num, 'S010', 'Argument name arg_name should be written in snake_case')
            if num in [v for v in func_mistakes['S011']]:
                print_error(filepath, num, 'S011', 'Variable var_name should be written in snake_case')
            if num in [v for v in func_mistakes['S012']]:
                print_error(filepath, num, 'S012', 'The default argument value is mutable')


def check_indentation(num, line, filename):
    if line.strip().isascii() and line.startswith(' ') \
            and line.find(line.strip()) % 4 != 0:
        print_error(filename, num, 'S002', 'Indentation is not a multiple of four')


def check_length(num, line, filename):
    if len(line.strip()) > 79:
        print_error(filename, num, 'S001', 'Too long')


def check_semicolon(num, line, filename):
    if ';' in line:
        if '#' in line and line.find('#') < line.find(';'):
            pass
        elif '"' in line and line.find(';') in range(line.index('"'), line.rindex('"')):
            pass
        elif "'" in line and line.find(';') in range(line.index("'"), line.rindex("'")):
            pass
        else:
            print_error(filename, num, 'S003', 'Unnecessary semicolon')


def check_comments(num, line, filename):
    if line.startswith('#'):
        pass
    elif '#' in line and line[line.find('#')-2:line.find('#')] != '  ':
        print_error(filename, num, 'S004', 'Less than two spaces before inline comments')


def check_todo(num, line, filename):
    if ('#' in line and 'todo' in line.lower()) and (line.find('#') < line.lower().find('todo')):
        print_error(filename, num, 'S005', 'TODO found')


def check_construction_spaces(num, line, filename):
    if ('class' in line or 'def' in line)\
            and (re.match(r'^class\s{2,}', line) or re.match(r'^def\s{2,}', line.lstrip())):
        print_error(filename, num, 'S007', 'Too many spaces after construction_name')


def check_class_name(num, line, filename):
    if 'class' in line and not re.match(r'^class\s+[A-Z]', line):
        print_error(filename, num, 'S008', 'Class name class_name should be written in CamelCase')


def check_func_name(num, line, filename):
    if 'def' in line \
            and not re.match(r'^def\s+[^A-Z]', line.lstrip()):
        print_error(filename, num, 'S009', 'Function name function_name should be written in snake_case')


def check_func_mistakes(py_file):

    func_mistakes = {'S010': [], 'S011': [], 'S012': []}

    tree = ast.parse(py_file.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for a in node.args.args:
                if not re.match(r'^[^A-Z]', a.arg):
                    func_mistakes['S010'].append(a.lineno)
                    continue

            for a in node.args.defaults:
                if isinstance(a, (ast.List, ast.Dict, ast.Set)):
                    func_mistakes['S012'].append(a.lineno)
                    continue

        for node in tree.body:
            for el in ast.walk(node):
                if isinstance(el, ast.Name):
                    if isinstance(el.ctx, ast.Store):
                        variable_name = el.id
                        if not re.match(r'^[^A-Z]', variable_name):
                            func_mistakes['S011'].append(el.lineno)

    return func_mistakes


def print_error(filename, count, code, message):
    return print(f'{filename}: Line {count}: {code} {message}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('location', type=str)

    args = parser.parse_args()

    if os.path.isfile(args.location) and args.location.endswith('.py'):
        analyze(args.location)
    elif os.path.isdir(args.location):
        with os.scandir(args.location) as entries:
            for entry in entries:
                if entry.name.endswith('.py'):
                    analyze(f"{args.location}\\{entry.name}")
