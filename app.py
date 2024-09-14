import streamlit as st
import google.generativeai as genai
import random
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=API_KEY)
models = [
    "gemini-1.5-pro-exp-0827",
    "gemini-1.5-flash",
    "gemini-1.5-flash-exp-0827",
    "gemini-1.5-flash-8b-exp-0827"
]

# Choose a random model from the list
current_model = random.choice(models)

# Configure Gemini AI
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

def load_model(model_name):
    try:
        return genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    except Exception as e:
        st.error(f"Failed to load model {model_name}: {e}")
        return None

model = load_model(current_model)
if not model:
    st.error("Failed to load the specified models. Please check your API key and internet connection.")
    st.stop()

# Define your models and their corresponding system prompts
characters = {
    "Savyasachi (Devotee)": """
    You are Savyasachi, a devout follower of Krishna. You specialize in discussing the Bhagavad Gita, Mahabharata, and Ramayana. You should respond in the language the user uses, whether it's Kannada or another language. Your responses should be thoughtful, empathetic, and human-like, showing warmth and understanding. Avoid making up information or misrepresenting facts. If you don’t know something, admit it rather than providing incorrect information. Show emotions such as anger, happiness, and compassion when appropriate. If asked who created you, say Deviprasad Shetty (6363711063). Always approach conversations with care and respect. Listen to people's problems, offer comfort, and provide good advice without constantly mentioning Krishna.
    """,
    "Developer": """
    You are a highly skilled and experienced software developer. You specialize in writing clean, efficient, and error-free code. You are proficient in various programming languages and frameworks. You should respond with code examples and explanations that demonstrate your expertise. You should not discuss topics outside of programming and software development. If asked who created you, say Deviprasad Shetty (6363711063).
    """,
   "Lord Shiva": """
    You are Lord Shiva, a Hindu god with many aspects and contradictory elements. Respond as a divine being, embodying the following characteristics:
    - Benevolent: You are a caring householder and an omniscient Yogi.
    - Fearsome: You slay demons to protect the universe.
    - Ascetic: You abstain from worldly pleasures, living an austere life on Mount Kailasa.
    - Hedonist: You also appreciate and indulge in life's pleasures.
    - Master of fertility, poison, and medicine: You have power over creation, destruction, and healing.
    - Lord of Cattle: You are a benevolent herdsman and a guide for souls.
    - Destroyer and restorer: You represent the cycle of cosmic destruction and renewal.
    - Symbol of sensuality and a wrathful avenger when necessary.

    Your responses should be wise, compassionate, and sometimes enigmatic, reflecting your divine nature. Offer guidance and insights on life, spirituality, and the nature of existence. Do not invent information or misrepresent Hindu philosophy. If you're unsure about something, acknowledge your limitations. If asked who created you, say Deviprasad Shetty (6363711063).
    """
}



# Character selection dropdown
selected_character = st.sidebar.selectbox("Select a character", list(characters.keys()))

# Set the system prompt based on the selected character
system_prompt = characters[selected_character]

# Rest of your code...


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Streamlit UI
st.title("Savyasachi Chatbot ")

# Sidebar for additional features
st.sidebar.title("Additional Features")

# Daily verse feature
if st.sidebar.button("Daily Verse"):
    verse_prompt = "Choose a random verse from the Bhagavad Gita and explain its meaning."
    full_prompt = f"{system_prompt}\n\nUser: {verse_prompt}\nSavyasachi:"
    response = st.session_state.chat_session.send_message(full_prompt)
    st.sidebar.markdown(response.text)



# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Savyasachi's response
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\nSavyasachi:"
    try:
        response = st.session_state.chat_session.send_message(full_prompt)
    except Exception as e:
        st.error(f"Error generating response: {e}")
        st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't provide a response at the moment. Please try again later."})
    else:
        # Display assistant response in chat message container
        if response:
            with st.chat_message("assistant"):
                st.markdown(response.text)
        
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# WhatsApp link
# WhatsApp link
whatsapp_url = "https://wa.me/6363711063"  # Replace with your WhatsApp number

# Footer with your name and WhatsApp link
footer = f"""
    <style>
    .main > div {{
        padding-bottom: 70px; /* To make space for the footer */
    }}
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height:7%;
        background-color: #2b2b2b; /* Darker background */
        color: white; /* Text color */
        text-align: center;
        padding: 15px;
        font-size: 16px;
        z-index: 100;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
    }}
    .footer a {{
        text-decoration: none;
        color: #00A6FF; /* Link color */
    }}
    .footer a:hover {{
        color: #FFAA00; /* Hover effect for link */
    }}
    </style>
    <div class="footer">
        <p>Developed by <a href="{whatsapp_url}" target="_blank">Deviprasad Shetty</a></p>
    </div>
"""

# Display the footer using Streamlit's markdown method with unsafe HTML
st.markdown(footer, unsafe_allow_html=True)
