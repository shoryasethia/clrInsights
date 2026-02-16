import io
import sys
import RestrictedPython
from typing import Any, Optional
from clrinsights.config import settings


class SafeCodeExecutor:
    """Execute Python code in a sandboxed environment."""
    
    # Allowed safe imports
    SAFE_BUILTINS = {
        'abs': abs,
        'all': all,
        'any': any,
        'bool': bool,
        'dict': dict,
        'enumerate': enumerate,
        'filter': filter,
        'float': float,
        'int': int,
        'len': len,
        'list': list,
        'map': map,
        'max': max,
        'min': min,
        'range': range,
        'round': round,
        'set': set,
        'sorted': sorted,
        'str': str,
        'sum': sum,
        'tuple': tuple,
        'zip': zip,
    }
    
    def __init__(self):
        self.timeout = settings.code_timeout_seconds
    
    def execute(
        self,
        code: str,
        context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Execute code in sandboxed environment.
        
        Args:
            code: Python code to execute
            context: Additional context variables
            
        Returns:
            Dictionary with 'output', 'result', 'error' keys
        """
        # Compile with RestrictedPython
        try:
            byte_code = RestrictedPython.compile_restricted(
                code,
                filename='<sandbox>',
                mode='exec'
            )
        except SyntaxError as e:
            return {
                'output': '',
                'result': None,
                'error': f"Syntax error: {str(e)}"
            }
        
        # Set up execution environment
        restricted_globals = {
            '__builtins__': self.SAFE_BUILTINS,
            '_getattr_': getattr,
            '_getitem_': lambda obj, key: obj[key],
            '_getiter_': iter,
            '_iter_unpack_sequence_': lambda x, spec: list(x),
        }
        
        # Add context if provided
        if context:
            restricted_globals.update(context)
        
        # Capture stdout
        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        
        try:
            sys.stdout = stdout_capture
            
            # Execute the code
            exec(byte_code, restricted_globals)
            
            # Get output
            output = stdout_capture.getvalue()
            
            # Get result if there's a 'result' variable
            result = restricted_globals.get('result', None)
            
            return {
                'output': output,
                'result': result,
                'error': None
            }
        
        except Exception as e:
            return {
                'output': stdout_capture.getvalue(),
                'result': None,
                'error': f"Execution error: {str(e)}"
            }
        
        finally:
            sys.stdout = old_stdout
            stdout_capture.close()
    
    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        Validate code without executing.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            RestrictedPython.compile_restricted(
                code,
                filename='<sandbox>',
                mode='exec'
            )
            return True, ""
        except Exception as e:
            return False, str(e)


# Global instance
code_executor = SafeCodeExecutor()
