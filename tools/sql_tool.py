from typing import Any
from clrinsights.data import db_manager


class SQLTool:
    """Tool for executing SQL queries against the database."""
    
    name = "sql_query"
    description = """Execute SQL query against the UPI transactions database.
    
Use this tool to query the database and retrieve data for analysis.
Always validate query syntax before execution.
Return results as structured data that can be further processed.

IMPORTANT: Use the complete schema context to understand:
- Valid column names and types
- NULL value conditions
- Valid values for categorical columns
- Query guidelines for common patterns
"""
    
    def __init__(self):
        self.db = db_manager
    
    def __call__(self, query: str) -> dict[str, Any]:
        """
        Execute SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            Dictionary with results or error
        """
        # Validate query first
        is_valid, error_msg = self.db.validate_query(query)
        if not is_valid:
            return {
                'success': False,
                'error': f"Invalid query: {error_msg}",
                'results': []
            }
        
        # Execute query
        try:
            results = self.db.execute_query(query)
            return {
                'success': True,
                'error': None,
                'results': results,
                'row_count': len(results)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_schema(self) -> str:
        """Get formatted schema for prompt context."""
        return self.db.get_schema_context()


sql_tool = SQLTool()
