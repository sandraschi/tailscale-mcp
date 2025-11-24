"""Final fix for indentation - ensure try/except blocks are properly indented."""

from pathlib import Path
import re

tool_files = [
    'device_tool.py', 'network_tool.py', 'monitor_tool.py', 'file_tool.py',
    'security_tool.py', 'backup_tool.py', 'performance_tool.py',
    'reporting_tool.py', 'integration_tool.py'
]

for tool_file in tool_files:
    file_path = Path(f'src/tailscalemcp/tools/{tool_file}')
    if not file_path.exists():
        continue
    
    content = file_path.read_text(encoding='utf-8')
    
    # Fix pattern: """\n        try:\n        if -> """\n        try:\n            if
    # The try block should be at 8 spaces, and its contents at 12 spaces
    content = re.sub(
        r'(""")\n        try:\n        (if|elif)',
        r'\1\n        try:\n            \2',
        content,
        flags=re.MULTILINE
    )
    
    # Fix: if/elif statements that should be indented under try
    # Pattern: \n        if operation == -> \n            if operation ==
    # But only after try:
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    
    for i, line in enumerate(lines):
        if '        try:' in line:
            in_try_block = True
            fixed_lines.append(line)
        elif in_try_block and line.strip().startswith(('if ', 'elif ', 'else:')):
            # These should be at 12 spaces (indented under try)
            if line.startswith('        ') and not line.startswith('            '):
                fixed_lines.append('            ' + line[8:])
            else:
                fixed_lines.append(line)
        elif in_try_block and line.strip() == 'except Exception as e:':
            in_try_block = False
            fixed_lines.append(line)
        elif in_try_block and line.strip().startswith('except'):
            in_try_block = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    file_path.write_text('\n'.join(fixed_lines), encoding='utf-8')
    print(f'Fixed {tool_file}')

print('Done')

