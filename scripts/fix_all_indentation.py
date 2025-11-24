"""Fix indentation in all tool files."""

from pathlib import Path

tool_files = [
    'device_tool.py', 'network_tool.py', 'monitor_tool.py', 'file_tool.py',
    'security_tool.py', 'automation_tool.py', 'backup_tool.py', 'performance_tool.py',
    'reporting_tool.py', 'integration_tool.py'
]

for tool_file in tool_files:
    file_path = Path(f'src/tailscalemcp/tools/{tool_file}')
    if not file_path.exists():
        continue
    
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    fixed_lines = []
    past_docstring = False
    
    for i, line in enumerate(lines):
        if 'async def tailscale_' in line:
            past_docstring = False
            fixed_lines.append(line)
            continue
        
        if not past_docstring and line.strip() == '"""' and i > 10:
            past_docstring = True
            fixed_lines.append(line)
            continue
        
        if past_docstring and line.strip():
            current_indent = len(line) - len(line.lstrip())
            if current_indent == 12 and not line.startswith('            """'):
                fixed_lines.append('        ' + line[12:])
            elif current_indent == 16:
                fixed_lines.append('            ' + line[16:])
            elif current_indent == 20:
                fixed_lines.append('                ' + line[20:])
            elif current_indent == 24:
                fixed_lines.append('                    ' + line[24:])
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    file_path.write_text('\n'.join(fixed_lines), encoding='utf-8')
    print(f'Fixed {tool_file}')

print('Done')


