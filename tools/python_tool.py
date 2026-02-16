from typing import Any
from clrinsights.sandbox import code_executor


class PythonTool:
    """Tool for executing Python code for data processing."""
    
    name = "execute_python"
    description = """Execute Python code to process and analyze data.
    
Use this tool for:
- Complex calculations that require Python
- Data transformations and aggregations
- Statistical computations

Code runs in a sandboxed environment with restricted imports.
Available builtins: abs, all, any, dict, enumerate, filter, float, int, len,
list, map, max, min, range, round, set, sorted, str, sum, tuple, zip

Store final result in a variable named 'result'.
"""
    
    def __call__(self, code: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: Python code to execute
            context: Additional context variables (e.g., data from SQL query)
            
        Returns:
            Dictionary with output, result, and error
        """
        # Validate code first
        is_valid, error = code_executor.validate_code(code)
        if not is_valid:
            return {
                'success': False,
                'output': '',
                'result': None,
                'error': f'Code validation failed: {error}'
            }
        
        # Execute code
        result = code_executor.execute(code, context)
        
        return {
            'success': result['error'] is None,
            'output': result['output'],
            'result': result['result'],
            'error': result['error']
        }


python_tool = PythonTool()
