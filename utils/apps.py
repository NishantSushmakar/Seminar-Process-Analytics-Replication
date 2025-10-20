from langgraph.graph import StateGraph
import pandas as pd
from utils.db import run_query_and_return_df
from utils.metrics import dataframe_similarity
from utils.helper import extract_sql_statement


class SimpleApp():
    def __init__(self, path_to_db,path_to_groud_truth_eventlog, llm_model):
        self.path_to_db = path_to_db
        self.llm_model = llm_model 
        self.path_to_groud_truth_eventlog=path_to_groud_truth_eventlog

    def get_sql_query(self, state):
        messages = state['messages']
        user_input = messages[-1]
        response = self.llm_model.invoke(user_input)
        #state['messages'].append(response.content) # appending AIMessage response to the AgentState
        state['agent_response']=response.content
        return state
    
    def run_sql_query(self, state):
        #messages = state['messages']
        #agent_response = messages[-1]
        # Make sure that only the SQL statement is extracted from the agent response
        agent_response=extract_sql_statement(state['agent_response'])
        #agent_response = 'SELECT * FROM "order" where "id"="o1"'
        try:
            df = run_query_and_return_df(path_to_db = self.path_to_db, query = agent_response)
            state['sqlexecuter'] = df
        except Exception as e:
            error_message = f"SQL_ERROR: {type(e).__name__}: {str(e)}"
            state['sqlexecuter'] = error_message
            print(f"SQL execution failed: {error_message}")
        return state
    
    def calculate_metrics(self, state):
        if type(state['sqlexecuter']) != str:
            df_true = pd.read_csv(self.path_to_groud_truth_eventlog, dtype='object')
            state['result'] = dataframe_similarity(df_true, state['sqlexecuter'])
        else:
            state['result'] = {}
        return state
        
    
    def invoke(self, AgentState):
        workflow = StateGraph(dict)
        # nodes
        workflow.add_node("agent", self.get_sql_query)
        workflow.add_node("sqlexecuter", self.run_sql_query)
        workflow.add_node("dfcomparator", self.calculate_metrics)
        # edges
        workflow.add_edge('agent', 'sqlexecuter')
        workflow.add_edge('sqlexecuter', 'dfcomparator')
        # entry, exit
        workflow.set_entry_point("agent")
        workflow.set_finish_point("dfcomparator")
        app = workflow.compile()
        app.invoke(AgentState)
        return AgentState

