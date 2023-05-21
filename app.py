import os
import openai
import streamlit as st
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from render import bot_msg_container_html_template, user_msg_container_html_template
from utils import semantic_search, get_page_contents
from prompts import human_template, system_message
import prompts


# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

embeddings = OpenAIEmbeddings()

st.header("RideBikes GPT")
resBox =st.empty()
gravelDB = Chroma(persist_directory=os.path.join('db', 'gravel'), embedding_function=embeddings)
gravel_retriever = gravelDB.as_retriever(search_kwargs={"k": 3})

# Define chat history storage
if "history" not in st.session_state:
    st.session_state.history = []

# Construct messages from chat history
def construct_messages(history):
    messages = [{"role": "system", "content": prompts.system_message}]
    
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    return messages

def gravel_handler(query):
    print("Using Buffett handler...")
    # Get relevant documents from Buffett's database
    relevant_docs = gravel_retriever.get_relevant_documents(query)

    # Use the provided function to prepare the context
    context = get_page_contents(relevant_docs)

    # Prepare the prompt for GPT-3.5-turbo with the context
    query_with_context = human_template.format(query=query, context=context)

    return {"role": "user", "content": query_with_context}

# Generate response to user prompt
def generate_response():


    st.session_state.history.append({
        "message": st.session_state.prompt,
        "is_user": True
    })

    # Perform semantic search and format results
    # search_results = semantic_search(st.session_state.prompt, top_k=3)
    # context = ""
    # for i, (title, transcript) in enumerate(search_results):
    #     context += f"Snippet from: {title}\n {transcript}\n\n"

    # Generate human prompt template and convert to API message format
    query_with_context = gravel_handler(st.session_state.prompt)

    # Convert chat history to a list of messages
    messages = construct_messages(st.session_state.history)
    messages.append(query_with_context)

    # Run the LLMChain
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    print(messages)

    # Parse response
    bot_response = response["choices"][0]["message"]["content"]
    st.session_state.history.append({
        "message": bot_response,
        "is_user": False
    })

    st.session_state.prompt = ""

st.markdown(
    """
    <style>
    .bottom-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 20px;
        background-color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create a container div with the custom CSS class

col1, col2= st.columns([99,1])



# User input prompt
user_prompt = st.text_input("Ask a question: ",
                            key="prompt",
                            placeholder="e.g. 'Which bike is the best?'",
                            
                            on_change=generate_response
                            )

# Display chat history
with col1:
    for message in st.session_state.history:
        if message["is_user"]:
            st.write(user_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)
        else:
            st.write(bot_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)
