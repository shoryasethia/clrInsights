from langgraph.graph import StateGraph, END
from clrinsights.agent.state import AgentState
from clrinsights.agent.nodes import (
    analyze_query_node,
    prepare_step_node,
    execute_sql_node,
    fix_sql_node,
    generate_visualizations_node,
    advance_step_node,
    generate_answer_node,
    route_after_analysis,
    route_after_sql,
)
from clrinsights.data import db_manager


def create_agent_graph() -> StateGraph:
    """
    Create and compile the agent workflow graph.
    
    Flow:
        analyze → prepare_step → execute_sql → route_after_sql
                                                 ├→ advance_step → prepare_step (loop for more steps)
                                                 ├→ fix_sql → execute_sql (retry loop, up to 3x)
                                                 └→ generate_viz → answer → END (all steps done)
        analyze → answer → END  (conversational / no SQL needed)
    """
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_query_node)
    workflow.add_node("prepare_step", prepare_step_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("fix_sql", fix_sql_node)
    workflow.add_node("generate_viz", generate_visualizations_node)
    workflow.add_node("advance_step", advance_step_node)
    workflow.add_node("answer", generate_answer_node)
    
    # Entry
    workflow.set_entry_point("analyze")
    
    # After analysis: either prepare first step or skip to answer
    workflow.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "prepare_step": "prepare_step",
            "answer": "answer"
        }
    )
    
    # prepare → execute SQL
    workflow.add_edge("prepare_step", "execute_sql")
    
    # After SQL: advance_step (more steps) | fix_sql (error) | generate_viz (all done)
    workflow.add_conditional_edges(
        "execute_sql",
        route_after_sql,
        {
            "advance_step": "advance_step",
            "fix_sql": "fix_sql",
            "generate_viz": "generate_viz"
        }
    )
    
    # fix_sql retries execution
    workflow.add_edge("fix_sql", "execute_sql")
    
    # advance_step loops back to prepare next step
    workflow.add_edge("advance_step", "prepare_step")
    
    # After viz generation, produce the answer
    workflow.add_edge("generate_viz", "answer")
    
    # Answer ends the workflow
    workflow.add_edge("answer", END)
    
    return workflow.compile()


async def run_agent(query: str, conversation_history: list = None, provider: str = "groq") -> dict:
    """
    Run the agent on a user query.
    
    Args:
        query: User question
        conversation_history: Previous messages
        provider: LLM provider to use ('gemini' or 'groq')
        
    Returns:
        Dictionary with answer, visualizations, metadata, and trace
    """
    graph = create_agent_graph()
    
    # Initialize trace
    trace = []
    
    # Initialize state
    initial_state: AgentState = {
        'messages': conversation_history or [],
        'query': query,
        'schema_context': db_manager.get_schema_context(),
        # Multi-step plan
        'steps': [],
        'current_step': 0,
        # Current step data
        'sql_query': None,
        'query_results': None,
        'python_code': None,
        'code_results': None,
        # Accumulated results
        'visualizations': [],
        'sql_queries': [],
        'all_query_results': [],
        # Control
        'answer': '',
        'error': None,
        'retries': 0,
        'should_continue': True,
        'provider': provider,
        'trace': trace
    }
    
    trace.append({
        'step': f'Initialized with provider: {provider.upper()}',
        'type': 'info',
        'prompt': None,
        'response': None
    })
    
    # Run graph
    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        trace.append({
            'step': f'Agent execution failed: {str(e)}',
            'type': 'error',
            'prompt': None,
            'response': str(e)
        })
        raise
    
    return {
        'answer': final_state.get('answer', ''),
        'visualizations': final_state.get('visualizations', []),
        'sql_queries': final_state.get('sql_queries', []),
        'all_query_results': final_state.get('all_query_results', []),
        # Keep single-value fields for backward compat
        'visualization': final_state.get('visualizations', [None])[0] if final_state.get('visualizations') else None,
        'sql_query': final_state.get('sql_queries', [None])[0] if final_state.get('sql_queries') else None,
        'query_results': final_state.get('query_results'),
        'error': final_state.get('error'),
        'messages': final_state.get('messages', []),
        'trace': final_state.get('trace', trace)
    }
