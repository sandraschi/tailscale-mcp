"""Fix indentation in generated tool files."""

import re
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
    in_function = False
    docstring_ended = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect start of async def
        if 'async def tailscale_' in line:
            in_function = True
            docstring_ended = False
            fixed_lines.append(line)
            i += 1
            continue
        
        # Detect end of function (next @ctx.mcp.tool() or end of register function)
        if in_function and ('def register_' in line or '@ctx.mcp.tool()' in line):
            in_function = False
            docstring_ended = False
        
        # Inside function body
        if in_function:
            # Check if we're past the docstring
            if '"""' in line and docstring_ended is False:
                if line.strip().endswith('"""') and line.strip() != '"""':
                    docstring_ended = True
                elif line.strip() == '"""':
                    # Check next few lines to see if docstring continues
                    j = i + 1
                    while j < min(i + 5, len(lines)):
                        if '"""' in lines[j]:
                            docstring_ended = True
                            break
                        j += 1
            elif docstring_ended is False and line.strip().startswith('"""'):
                docstring_ended = True
            
            # Fix indentation: function body should be indented 8 spaces (2 levels)
            # But parameters and docstring are already correct
            if docstring_ended and line.strip() and not line.strip().startswith('#'):
                # Function body lines that start with 12 spaces should be 8 spaces
                if line.startswith('            ') and not line.startswith('            """'):
                    fixed_lines.append('        ' + line[12:])
                # Lines with 16 spaces should be 12 spaces (nested blocks)
                elif line.startswith('                '):
                    fixed_lines.append('            ' + line[16:])
                # Lines with 20 spaces should be 16 spaces (double nested)
                elif line.startswith('                    '):
                    fixed_lines.append('                ' + line[20:])
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    file_path.write_text('\n'.join(fixed_lines), encoding='utf-8')
    print(f'Fixed {tool_file}')

print('Done fixing indentation')


