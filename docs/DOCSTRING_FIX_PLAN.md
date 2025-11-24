# Docstring Fix Plan - Tailscale MCP Tools

**Status:** In Progress  
**Priority:** Critical  
**Issue:** All tool docstrings are too brief and missing required FastMCP 2.12 standards

---

## Current Problems

### Issues Found:
1. **Too Brief** - Docstrings are 50-100 lines, need 200+ lines for complex tools
2. **Missing Examples** - No examples for individual operations
3. **Incomplete Parameter Docs** - Missing constraints, defaults, required/optional status
4. **Missing Return Details** - Vague return descriptions, no structure details
5. **Missing Usage Section** - No guidance on when/how to use
6. **Missing Notes Section** - No important considerations
7. **Missing Operation Details** - Operations listed but not fully described

---

## Required Sections (FastMCP 2.12 Standard)

Each tool docstring MUST include:

1. **Brief Description** (1-2 sentences)
2. **Detailed Description** (2-5 sentences explaining WHAT, WHY, WHEN)
3. **SUPPORTED OPERATIONS** - Detailed list with full descriptions
4. **Parameters** - Complete documentation with:
   - Type information
   - Default values
   - Required vs optional
   - Constraints and valid values
   - When each parameter is used
5. **Returns** - Detailed structure for each operation
6. **Usage** - When and how to use the tool
7. **Examples** - At least 3 examples per operation type
8. **Raises** - All possible exceptions
9. **Notes** - Important considerations, limitations, best practices

---

## Implementation Plan

### Phase 1: Create Comprehensive Template
- Create 200+ line docstring template for `tailscale_device`
- Include all required sections
- Provide examples for each operation

### Phase 2: Apply to All Tools
- Update all 12 portmanteau tools
- Ensure consistency across all tools
- Verify all operations documented

### Phase 3: Validation
- Check docstring length (200+ lines for complex tools)
- Verify all operations have examples
- Ensure parameter documentation complete
- Test that docstrings render correctly

---

## Template Structure

```python
"""Comprehensive [tool name] operations.

[2-5 sentence detailed description explaining what the tool does, why it exists,
and when to use it. Provide context and use cases.]

SUPPORTED OPERATIONS:

This portmanteau tool provides [N] operations organized into categories:

[Category 1]:
- operation1: [Full description with requirements and use cases]
- operation2: [Full description with requirements and use cases]

[Category 2]:
- operation3: [Full description with requirements and use cases]

[Continue for all operations...]

Args:
    operation: Operation to perform. MUST be one of: [list all operations]
        - operation1: [Full description]
        - operation2: [Full description]
        [Continue for all operations...]
    
    param1: Parameter description (required for operation1, operation2)
        - Type: str
        - Required: Yes (for operation1, operation2)
        - Valid values: [list valid values]
        - Default: None
        - Constraints: [any constraints]
    
    param2: Parameter description (optional, default: value)
        - Type: bool
        - Required: No
        - Default: False
        - Used by: operation3, operation4

[Continue for all parameters...]

Returns:
    Dictionary containing operation results. Structure varies by operation:
    
    For operation1:
        {
            "operation": "operation1",
            "result": [result data],
            "metadata": [additional info]
        }
    
    For operation2:
        {
            "operation": "operation2",
            "data": [result data],
            "count": int,
            "filters": {filter info}
        }
    
    [Continue for all operations...]

Raises:
    TailscaleMCPError: If operation fails or invalid parameters provided
    ValueError: If required parameters are missing for the specified operation
    NotFoundError: If requested resource (device, service, etc.) not found

Usage:
    This tool is used when you need to [explain primary use case]. It works by
    [explain mechanism]. Best practices include [list recommendations].
    
    Common scenarios:
    - Scenario 1: [Description of when to use]
    - Scenario 2: [Another use case]
    - Scenario 3: [Special considerations]
    
    Workflow example:
    1. First, use operation1 to [action]
    2. Then, use operation2 to [action]
    3. Finally, use operation3 to [action]

Examples:
    Basic operation1 usage:
        result = await tailscale_device(
            operation="operation1",
            param1="value1"
        )
        # Returns: {
        #     "operation": "operation1",
        #     "result": {...},
        #     "metadata": {...}
        # }
    
    Advanced operation1 with filters:
        result = await tailscale_device(
            operation="operation1",
            param1="value1",
            param2=True,
            param3=["filter1", "filter2"]
        )
        # Returns filtered results with metadata
    
    Operation2 with all parameters:
        result = await tailscale_device(
            operation="operation2",
            param1="value1",
            param4="value4"
        )
        # Returns operation2 specific structure
    
    Error handling:
        try:
            result = await tailscale_device(
                operation="operation1",
                param1="invalid"
            )
        except TailscaleMCPError as e:
            print(f"Operation failed: {e}")
        # Handles errors gracefully

Notes:
    - Important consideration 1: [Details]
    - Important consideration 2: [Details]
    - Performance: [Performance implications]
    - Security: [Security considerations]
    - Limitations: [Any limitations]
    - Best practices: [Recommendations]
    - Related tools: [Cross-references to other tools]
"""
```

---

## Progress Tracking

- [ ] tailscale_device - Comprehensive docstring (200+ lines)
- [ ] tailscale_network - Comprehensive docstring (200+ lines)
- [ ] tailscale_monitor - Comprehensive docstring (200+ lines)
- [ ] tailscale_file - Comprehensive docstring (200+ lines)
- [ ] tailscale_security - Comprehensive docstring (200+ lines)
- [ ] tailscale_automation - Comprehensive docstring (200+ lines)
- [ ] tailscale_backup - Comprehensive docstring (200+ lines)
- [ ] tailscale_performance - Comprehensive docstring (200+ lines)
- [ ] tailscale_reporting - Comprehensive docstring (200+ lines)
- [ ] tailscale_integration - Comprehensive docstring (200+ lines)
- [ ] tailscale_help - Comprehensive docstring (200+ lines)
- [ ] tailscale_status - Comprehensive docstring (200+ lines)

---

**Next Step:** Create comprehensive docstring for tailscale_device as template

