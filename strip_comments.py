utf-8import os
import re
import tokenize
import io
def strip_js_comments(code):
    pattern = re.compile(r"""(?:'[^'\\]*(?:\\.[^'\\]*)*'|"[^"\\]*(?:\\.[^"\\]*)*"|`[^`\\]*(?:\\.[^`\\]*)*`)|(?://[^\n]*|/\*[\s\S]*?\*/)""")
    def replacer(match):
        s = match.group(0)
        if s.startswith('/') and not s.startswith('// eslint'):
            return ''
        return s
    return pattern.sub(replacer, code)
def strip_py_comments(code):
    result = []
    try:
        tokens = tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline)
        last_lineno = -1
        last_col = 0
        for tok in tokens:
            token_type = tok.type
            token_string = tok.string
            start_line, start_col = tok.start
            end_line, end_col = tok.end
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                result.append(" " * (start_col - last_col))
            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING and tok.line.strip().startswith(token_string):
                pass
            else:
                result.append(token_string)
            last_lineno = end_line
            last_col = end_col
        clean_lines = [line for line in "".join(result).splitlines() if line.strip()]
        return "\n".join(clean_lines)
    except Exception as e:
        return re.sub(r'(?m)^ *#.*\n?', '', code)
def process_dir(root_dir):
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in dirs: dirs.remove('node_modules')
        if 'dist' in dirs: dirs.remove('dist')
        if '.git' in dirs: dirs.remove('.git')
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                cleaned = strip_js_comments(code)
                cleaned = '\n'.join([line for line in cleaned.splitlines() if line.strip()])
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
            elif file.endswith('.py'):
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                cleaned = strip_py_comments(code)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
process_dir('C:/Users/lenovo/.gemini/antigravity/scratch/news-pulse')
print('Comments stripped successfully!')