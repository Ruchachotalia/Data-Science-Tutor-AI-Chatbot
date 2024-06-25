import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder

def main():
    st.title("💬 Data Science Tutor")

    # Load API key from Streamlit's secrets
    openai_api_key = st.secrets["OPENAI_API_KEY"]

    # Initialize OpenAI and LangChain client
    client = OpenAI(api_key=openai_api_key)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)

    # Initialize session state for conversations and buffer memory
    if 'data_sessions' not in st.session_state:
        st.session_state.data_sessions = {}
    if 'current_session' not in st.session_state:
        st.session_state['current_session'] = []
    if 'buffer_memory' not in st.session_state:
        st.session_state.buffer_memory = ConversationBufferWindowMemory(k=3, return_messages=True)

    # Conversation chain configuration
    system_msg_template = SystemMessagePromptTemplate.from_template(template="Answer the question using the provided context.")
    human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
    prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])
    conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

    # Manage conversation sidebar
    manage_conversations_sidebar()

    st.subheader("Ask me anything about Data Science, or try executing Python code!")

    with st.form(key='user_input_form'):
        user_input = st.text_area("Enter your question or Python code:", key='user_input')
        #code_flag = st.checkbox("Check if input is Python code to execute")
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        with st.spinner("Thinking..."):
            response = conversation.predict(input=f"Context: \n\n Query: {user_input}")

        st.session_state['current_session'].append((user_input, response))
        st.experimental_rerun()


    if st.session_state['current_session']:
        st.write("Conversation History:")
        for i, (q, a) in enumerate(reversed(st.session_state['current_session']), start=1):
            message(a, key=f"{i}_response")
            message(q, is_user=True, key=f"{i}_query")

def exec_code(user_code):
    """ Execute Python code in a restricted environment and return the output. """
    try:
        exec(user_code, {"__builtins__": {}}, locals())
        return locals().get('output', 'No output produced or output variable not set')
    except Exception as e:
        return f"Error during execution:\n{str(e)}"

def manage_conversations_sidebar():
    st.sidebar.header("About Data Science Tutor")
    st.sidebar.info("Welcome to AI tutor, I will to help you understand complex Data Science concepts and solve problems.")

    st.sidebar.header("Instructions:")
    st.sidebar.markdown("Ask a general question, type 'What is the purpose of feature scaling in machine learning?' to try it out, or even execute a Python code.")

    st.sidebar.header("Conversation Management:")
    session_name = st.sidebar.text_input("Session Name:", key="session_name")
    if st.sidebar.button("Save Session"):
        if session_name:
            st.session_state['data_sessions'][session_name] = st.session_state['current_session'].copy()
            st.sidebar.success("Session Saved!")
    selected_session = st.sidebar.selectbox("Select a Session", options=list(st.session_state['data_sessions'].keys()))
    if st.sidebar.button("Delete Session"):
        if selected_session in st.session_state['data_sessions']:
            del st.session_state['data_sessions'][selected_session]
            st.sidebar.success("Session Deleted!")
            st.experimental_rerun()
    if st.sidebar.button("Load Session"):
        if selected_session in st.session_state['data_sessions']:
            st.session_state['current_session'] = st.session_state['data_sessions'][selected_session].copy()
            st.experimental_rerun()
    if st.sidebar.button("Start New Session"):
        st.session_state['current_session'] = []
        st.experimental_rerun()

if __name__ == "__main__":
    main()
