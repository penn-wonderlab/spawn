import streamlit as st
from groq import Groq

from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

st.set_page_config(layout="wide")

st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.header('Spawn', divider='rainbow')
with st.expander("Read more about the idea behind Spawn."):
    st.markdown("*What if multiple AI agents can be configured to guide the student to consider an idea in different "
                "ways?* Each agent has different specialties and can access different tools. They work collaboratively "
                "to advise the student to improve their ideas.")

with st.sidebar:
    API_KEY = st.text_input("First, enter your Groq API key.", type="password")
    st.write("No API key? Get yours [here](https://console.groq.com/keys).")
    add_button = False
    st.subheader("Set contexts:")
    with st.container(border=True):
        with st.container(border=True):
            st.write("Context #1")
            col1, col2 = st.columns(2)
            with col1:
                identity = st.text_input("Identity", key="id0", value="6 year old")
            with col2:
                time = st.text_input("Time/Year", key="time0", value="2024")
            subject = st.text_input("Relationship to Subject", key="sub0", value="interested in dinosaurs and trucks")
        if 'selectbox_count' not in st.session_state:
            st.session_state.selectbox_count = 0


        def add_callback():
            st.session_state.selectbox_count += 1


        for i in range(st.session_state.selectbox_count):
            with st.container(border=True):
                st.write(f"Context #{i + 2}")
                col1, col2 = st.columns(2)
                with col1:
                    identity = st.text_input("Identity", key=f"id{i + 1}")
                with col2:
                    time = st.text_input("Time/Year", key=f"time{i + 1}")
                subject = st.text_input("Relationship to Subject", key=f"sub{i + 1}")

        engine = st.empty()  # Assuming engine is a Streamlit container
        add_clicked = engine.button("Add another context", on_click=add_callback, help="Add a new test", key="Add")
        conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

client = Groq(
    api_key=API_KEY,
)

if API_KEY:
    groq_chat = ChatGroq(
        groq_api_key=API_KEY,
        model_name="llama3-8b-8192"
    )

chat, essay = st.columns(2)

if 'transfer_clicked' not in st.session_state:
    st.session_state.transfer_clicked = False


def transfer_clicked():
    st.session_state.transfer_clicked = True


with chat:
    st.subheader("Chat")

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history",
                                            return_messages=True)

    chatbox = st.container(height=300)

    # this is for display
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with chatbox.chat_message(message["role"]):
            st.markdown(message["content"])

    # this is for langchain
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            memory.save_context({'input': message['human']}, {'output': message['AI']})

    if prompt := st.chat_input("Say something..."):
        # Display user message in chat message container
        with chatbox.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        for j in range(0, st.session_state.selectbox_count + 1):
            system_prompt = "You are a creative assistant who is an expert in helping someone think about ideas " \
                            "from different, fresh angles. Below is one piece of text from a grade 9 student who " \
                            "is studying science. It might be a question, an opinion, or an explanatory theory. " \
                            "You will take a look at the text and say something equivalent back to the student. " \
                            "Your output should have equivalent length; do not make it a long speech. Don't make " \
                            "your output a response to the student, simply output a statement. Use a similar " \
                            "tone as the student. I will ask you to speak as a particular character from a " \
                            "particular context. Please draw on knowledge this particular character would have " \
                            "when considering the particular context. In other words, you do not need to limit " \
                            "your response to the student's text while maintaining a strong connection with the " \
                            "student's idea. \n" + \
                            f"your current character and context: you are a " + st.session_state[f"id{j}"] \
                            + " who is " + st.session_state[f"sub{j}"] + " in the time period " \
                            + st.session_state[f"time{j}"] + "\n" + "Again, please keep your response brief," \
                                                                    " equivalent in length with the student text," \
                                                                    " and remember to stay in character."
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    # This is the persistent system prompt that is always included at the start of the chat.
                    SystemMessage(content=system_prompt),
                    # This placeholder will be replaced by the actual chat history during the conversation. It
                    # helps in maintaining context.
                    MessagesPlaceholder(variable_name="chat_history"),
                    # This template is where the user's current input will be injected into the prompt.
                    HumanMessagePromptTemplate.from_template("{human_input}"),
                ]
            )
            # Create a conversation chain using the LangChain LLM (Language Learning Model)
            conversation = LLMChain(
                llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
                prompt=prompt_template,  # The constructed prompt template.
                verbose=True,  # Enables verbose output, which can be useful for debugging.
                memory=memory,  # The conversational memory object that stores and manages the conversation history.
            )

            # The chatbot's answer is generated by sending the full prompt to the Groq API.
            response = conversation.predict(human_input=prompt)
            message = {'human': prompt, 'AI': response}
            st.session_state.chat_history.append(message)
            chat_response = "**" + st.session_state[f"id{j}"] + "** who is **" + st.session_state[f"sub{j}"] + \
                            "** during **" + st.session_state[f"time{j}"] + "**: " + response
            # Display assistant response in chat message container
            with chatbox.chat_message("assistant"):
                st.markdown(chat_response)

                st.button(":arrow_right:", help="Transfer bot response over to Essay.",
                          on_click=transfer_clicked)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": chat_response})

with essay:
    st.subheader("Essay")
    if st.session_state.transfer_clicked:
        st.session_state.student_text += st.session_state.messages[-1]['content'].split(": ", 1)[1]
    st.text_area("essay", label_visibility="collapsed", height=355, key="student_text")
