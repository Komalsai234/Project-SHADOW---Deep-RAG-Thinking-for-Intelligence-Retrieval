import streamlit as st
import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


logging.basicConfig(level=logging.INFO)

from src.pipeline.orchestrator import PipelineOrchestrator

st.markdown("""
    <style>
    /* Light neutral theme */
    .stApp {
        background-color: #f5f5f5;
        color: #333333;
        font-family: 'Roboto', sans-serif;
        max-width: 800px;
        margin: auto;
        padding: 20px;
    }
    /* Title styling */
    h1 {
        color: #006064;
        text-align: center;
        font-size: 2em;
        margin-bottom: 30px;
    }
    /* Inputs */
    .stSelectbox, .stTextInput {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 15px;
    }
    .stSelectbox label, .stTextInput label {
        color: #006064;
        font-weight: bold;
    }
    /* Button */
    .stButton>button {
        background-color: #00838f;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1em;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #006064;
    }
    /* Response area */
    .stTextArea {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
        min-height: 200px;
        max-height: 300px;
        overflow-y: auto;
        font-size: 0.95em;
        color: #333333;
    }
    .stTextArea label {
        color: #006064;
        font-weight: bold;
    }
    /* Error and info */
    .stAlert {
        border-radius: 8px;
        padding: 10px;
    }
    /* Checkbox */
    .stCheckbox {
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_pipeline():
    logging.info("Creating new PipelineOrchestrator instance")
    return PipelineOrchestrator()

def main():
    st.title("Project SHADOW - Intelligence Query")
    
    pipeline = get_pipeline()

    agent_level = st.selectbox(
        "Agent Clearance Level",
        options=[1, 2, 3, 4, 5, 7, 9],
        index=0,
        help="Select your clearance level to access intelligence."
    )
    
    query = st.text_input(
        "Enter Query",
        placeholder="e.g., What is the protocol for emergency extraction?",
        value=""
    )
    
    if st.button("Submit"):
        if not query:
            st.warning("Please enter a query to proceed.")
            return
        
        with st.spinner("Processing query..."):
            try:
                response = pipeline.process_query(query=query, agent_level=agent_level)
                
                if response:
                    st.markdown("### Response")
                    st.markdown(response, unsafe_allow_html=True)
                else:
                    st.warning("No response generated. Please check your query or clearance level.")
            except Exception as e:
                st.error(f"Error processing query: {str(e)}\n\nCheck console logs for details. Ensure entity_graph.pkl exists and secret_info_manual.txt is valid.")
                logging.error(f"Streamlit query error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()