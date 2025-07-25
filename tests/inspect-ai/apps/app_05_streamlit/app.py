import streamlit as st

st.title("My Simple Streamlit App")

user_name = st.text_input("Enter your name", "Type your name here...")

# Add a slider widget
user_age = st.slider("Select your age", 0, 100, 25)

# Display the user's input
st.write(f"Hello, {user_name}! You are {user_age} years old.")
