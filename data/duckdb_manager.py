import json
import duckdb
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional
from clrinsights.config import settings


class DuckDBManager:
    """Manages DuckDB connection and query execution for CSV data analysis."""
    
    def __init__(self):
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
        self.schema: dict[str, Any] = {}
        self._load_schema()
        self._initialize_connection()
    
    def _load_schema(self) -> None:
        """Load schema definition from JSON file."""
        schema_path = Path(settings.schema_absolute_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
    
    def _initialize_connection(self) -> None:
        """Initialize DuckDB connection and load CSV data."""
        csv_path = Path(settings.csv_absolute_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        self.conn = duckdb.connect(':memory:')
        
        table_name = self.schema.get('table_name', 'transactions')
        
        # Load CSV into a temp table first
        self.conn.execute(f"""
            CREATE TABLE _raw_import AS 
            SELECT * FROM read_csv_auto('{csv_path}', header=true)
        """)
        
        # Get actual column names and create normalized aliases
        raw_cols = [desc[0] for desc in self.conn.execute("SELECT * FROM _raw_import LIMIT 0").description]
        
        # Build column rename: replace spaces and special chars with underscores, lowercase
        col_renames = []
        for col in raw_cols:
            clean = col.strip().replace(' ', '_').replace('(', '').replace(')', '').lower()
            col_renames.append(f'"{ col }" AS {clean}')
        
        # Create the final table with clean column names
        select_clause = ', '.join(col_renames)
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT {select_clause} FROM _raw_import
        """)
        self.conn.execute("DROP TABLE _raw_import")
        
        # Store actual column names for schema context
        self._actual_columns = [desc[0] for desc in self.conn.execute(f"SELECT * FROM {table_name} LIMIT 0").description]
    
    def get_schema_context(self) -> str:
        """Get formatted schema context for LLM prompts."""
        table_name = self.schema['table_name']
        
        # Get actual columns from DB to ensure accuracy
        actual_cols = getattr(self, '_actual_columns', [])
        
        schema_text = f"# Database Schema\n\n"
        schema_text += f"Table: `{table_name}`\n"
        schema_text += f"Description: {self.schema['description']}\n\n"
        
        # List actual DB column names prominently
        if actual_cols:
            schema_text += f"## Exact Column Names (use these EXACTLY in SQL)\n"
            schema_text += f"{', '.join(actual_cols)}\n\n"
        
        schema_text += "## Column Details\n\n"
        
        for col in self.schema['columns']:
            # Map schema name to actual DB name
            schema_name = col['name']
            # Find matching actual column
            matched = schema_name
            for ac in actual_cols:
                if ac == schema_name.lower().replace(' ', '_').replace('(', '').replace(')', ''):
                    matched = ac
                    break
            
            schema_text += f"- **{matched}** ({col['type']}): {col['description']}\n"
            if 'example' in col:
                schema_text += f"  - Example: `{col['example']}`\n"
            if 'valid_values' in col:
                schema_text += f"  - Valid values: {', '.join(str(v) for v in col['valid_values'])}\n"
            if col.get('nullable'):
                schema_text += f"  - Nullable: Yes"
                if 'null_condition' in col:
                    schema_text += f" ({col['null_condition']})"
                schema_text += "\n"
            schema_text += "\n"
        
        schema_text += "## Important Notes\n"
        for note in self.schema['important_notes']:
            schema_text += f"- {note}\n"
        
        schema_text += "\n## Query Guidelines\n"
        for guideline in self.schema['query_guidelines']:
            schema_text += f"- {guideline}\n"
        
        schema_text += f"\n## CRITICAL: Column names are lowercase with underscores. Use them exactly as listed above.\n"
        
        return schema_text
    
    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            
        Returns:
            List of dictionaries representing query results
            
        Raises:
            Exception: If query execution fails
        """
        try:
            result = self.conn.execute(query).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            
            # Convert to list of dictionaries with JSON-safe values
            rows = []
            for row in result:
                safe_row = {}
                for col, val in zip(columns, row):
                    if isinstance(val, (datetime, date, time)):
                        safe_row[col] = val.isoformat()
                    elif isinstance(val, timedelta):
                        safe_row[col] = str(val)
                    elif isinstance(val, Decimal):
                        safe_row[col] = float(val)
                    elif isinstance(val, bytes):
                        safe_row[col] = val.hex()
                    else:
                        safe_row[col] = val
                rows.append(safe_row)
            return rows
        
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validate SQL query without executing it.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use EXPLAIN to validate query
            self.conn.execute(f"EXPLAIN {query}")
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def get_table_info(self) -> dict[str, Any]:
        """Get table metadata including row count and column info."""
        table_name = self.schema['table_name']
        
        # Get row count
        row_count = self.conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]
        
        # Get column information
        columns = self.conn.execute(
            f"PRAGMA table_info('{table_name}')"
        ).fetchall()
        
        return {
            'table_name': table_name,
            'row_count': row_count,
            'columns': [
                {'name': col[1], 'type': col[2], 'nullable': not col[3]}
                for col in columns
            ]
        }
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


# Global instance
db_manager = DuckDBManager()
