import streamlit as st
from groq import Groq

API_KEY = st.text_input("First, enter your Groq API key.", type="password")
st.write("No API key? Get yours [here](https://console.groq.com/keys).")

client = Groq(
    api_key=API_KEY,
)

summ_input = st.text_area("Enter topic summary.")

with st.form("lect_form"):
    st.write("Generate a lecture outline based on the topic.")
    submitted = st.form_submit_button("Generate")
    if submitted:
        lect_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": 'Create a suggested outline for a lecture on "' + summ_input + '"',
        }], model="llama3-8b-8192", )
        st.write(lect_creation.choices[0].message.content)

with st.form("slides_form"):
    st.write("Generate potential slides based on the topic.")
    submitted = st.form_submit_button("Generate")
    if submitted:
        slides_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": 'Create class slides from this summary: "' + summ_input + '"',
        }], model="llama3-8b-8192", )
        st.write(slides_creation.choices[0].message.content)

with st.form("act_form"):
    st.write("Generate an interactive activity based on the topic.")
    submitted = st.form_submit_button("Generate")
    if submitted:
        act_creation = client.chat.completions.create(messages=[{
            "role": "user",
            "content": 'Create an interactive activity based on "' + summ_input + '"',
        }], model="llama3-8b-8192", )
        st.write(act_creation.choices[0].message.content)