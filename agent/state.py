from typing import TypedDict, Annotated, Sequence
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the agent graph."""
    
    # Messages in the conversation
    messages: Annotated[Sequence[dict], add_messages]
    
    # Current user query
    query: str
    
    # Schema context for LLM
    schema_context: str
    
    # --- Multi-step plan ---
    # List of planned steps from analysis
    steps: list[dict]
    
    # Current step index
    current_step: int
    
    # --- Current step data (overwritten each iteration) ---
    # SQL query for current step
    sql_query: str | None
    
    # Query results for current step
    query_results: list[dict] | None
    
    # Python code to execute
    python_code: str | None
    
    # Code execution results
    code_results: dict | None
    
    # --- Accumulated results across all steps ---
    # All generated visualizations (base64 strings)
    visualizations: list[str]
    
    # All executed SQL queries
    sql_queries: list[str]
    
    # All query result sets
    all_query_results: list[list[dict]]
    
    # Final answer for user
    answer: str
    
    # Error messages
    error: str | None
    
    # Number of retries attempted
    retries: int
    
    # Whether to continue workflow
    should_continue: bool
    
    # LLM provider to use ('gemini' or 'groq')
    provider: str
    
    # Execution trace for debugging
    trace: list[dict]
