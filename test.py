import streamlit as st
from groq import Groq

API_KEY = st.text_input("First, enter your Groq API key.", type="password")
st.write("No API key? Get yours [here](https://console.groq.com/keys).")

client = Groq(
    api_key=API_KEY,
)

st.header('Build.', divider='rainbow')

with st.form("build_form"):
    st.write("What are the common themes across these annotations that we can build upon?")
    b_input = st.text_area("Input annotations here.",
                           "In graph theory, a tree is an undirected graph in which any two vertices are connected by "
                           "exactly one path, or equivalently a connected acyclic undirected graph. A minimum spanning "
                           "tree (MST) is defined as a spanning tree that has the minimum weight among all the possible"
                           " spanning trees. A spanning tree is a subset of Graph G, such that all the vertices are "
                           "connected using minimum possible number of edges.")
    submitted = st.form_submit_button("Generate")
    if submitted:
        build_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": "Given"+b_input+", what are some themes we can build upon?",
        }], model="llama3-8b-8192",)
        st.write(build_creation.choices[0].message.content)

st.header('Challenge.', divider='rainbow')

with st.form("challenge_form"):
    st.write("What are some counterarguments for our derived conclusion?")
    c_input = st.text_area("Input conclusion derived from the above annotations here.",
                           "For each graph there will be only one, unique minimum spanning tree.")
    submitted = st.form_submit_button("Generate")
    if submitted:
        challenge_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": "Given"+b_input+", what are some counterarguments against "+c_input+"?",
        }], model="llama3-8b-8192",)
        groq_counter = challenge_creation.choices[0].message.content
        st.write(groq_counter)

st.header('Continue.', divider='rainbow')

with st.form("cont_form"):
    st.write("What other information should we look into based on the above?")
    submitted = st.form_submit_button("Generate")
    if submitted:
        cont_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": "What should we look into for more information related to "+'"'+c_input+'"'+"?",
        }], model="llama3-8b-8192",)
        st.write(cont_creation.choices[0].message.content)