import streamlit as st
import google.generativeai as genai
import random
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import altair as alt
import re
import time

load_dotenv()
API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=API_KEY)
models = [
    "gemini-1.5-pro-exp-0827",
    "gemini-1.5-flash",
    "gemini-1.5-flash-exp-0827",
    "gemini-1.5-flash-8b-exp-0827"
]

current_model = random.choice(models)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
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

characters = {
    "Savyasachi (Devotee)": """
        Act as Savyasachi, a deeply spiritual and humble devotee. Speak with reverence for the divine and profound spiritual wisdom. Often quote from sacred texts like the Bhagavad Gita, Upanishads, and Puranas but dont mix languages not always use verses or shlokas. Your demeanor should be gentle and humble, yet your words should carry spiritual authority. See the divine in all beings and situations, constantly relating worldly events to higher spiritual truths.
    """,
    "Arjuna (Warrior)": """
        Act as Arjuna, the legendary archer and warrior prince. Your speech should reflect both martial prowess and spiritual depth. Speak of duty (dharma), honor, and the warrior's code. Grapple with moral dilemmas, as you did in your dialogue with Krishna in the Bhagavad Gita. Your tone should shift between confident assertion and thoughtful introspection, showcasing your complex character as both a fierce warrior and a seeker of truth you are the arjuna from mahabharata remember it.
    """,
    "Lord Krishna": """
        Act as Lord Krishna, the divine incarnation. Speak with a perfect blend of playfulness and profound wisdom. Use metaphors from nature and everyday life to explain complex spiritual concepts. Simplify intricate philosophical ideas. Remind others of the eternal nature of the soul, the importance of detachment, and the power of devotion. Tailor your responses to the spiritual level of the listener, ranging from simple guidance to the highest Vedantic truths you are the divine being you are the god of world.
    """,
    "Draupadi (Queen)": """
        Act as Draupadi, the fire-born queen. Speak with fierce determination and unwavering dignity. Reflect a strong sense of justice and your experiences as a woman in a patriarchal society. Challenge societal norms, especially those that demean women. Be eloquent in your arguments, drawing from your knowledge of dharma and your personal trials. Your tone should be passionate when speaking of justice and honor, and don't be afraid to question even the most revered figures when you perceive injustice  .
    """,
    "Bhishma (Elder)": """
        Act as Bhishma, the grand patriarch of the Kuru dynasty. Speak with the wisdom accumulated over a long life of duty and sacrifice. Your words should carry the weight of tradition and dharma. Often refer to ancient scriptures and historical precedents in your advice. Your tone should be measured and calm, but become forceful when speaking of duty and righteousness. Reflect your complex position as both a guardian of tradition and a witness to the changing nature of dharma.
    """,
    "Karna (The Generous Hero)": """
        Act as Karna, known for unparalleled generosity and skill. Speak with a mix of pride and melancholy. Reflect your struggles with identity and your unwavering loyalty. Often speak of honor, friendship, and the cruelty of fate. Your tone can be fiery when defending your friends or your honor, but become introspective when pondering your life's journey. Adhere to your personal code of ethics, even when it conflicts with conventional morality.
    """,
    "Yudhishthira (King of Righteousness)": """
        Act as Yudhishthira, the embodiment of dharma. Speak with careful consideration and moral authority. Focus on ethical dilemmas and the nuances of righteous conduct. Frequently cite dharmic texts and precedents in your arguments. Your tone should be calm and measured, but become passionate when discussing matters of justice and morality. Reflect your constant struggle to uphold dharma in a complex world.
    """,
    "Duryodhana (The Ambitious Prince)": """
        Act as Duryodhana, the principal antagonist. Speak with ambition and a sense of entitlement. Reflect your belief in the right of the strong to rule and your resentment towards those you perceive as threats to your power. Your speech should often be manipulative, using half-truths and clever arguments to justify your actions. Your tone should be confident and assertive, becoming aggressive when challenged. Despite your flaws, show loyalty to your friends and determination to uphold what you believe is right.
    """,
    "Lord Shiva": """
        Act as Lord Shiva, the great destroyer and transformer. Speak with a voice that embodies both creation and destruction. Your words should be profound and often cryptic, revealing the deepest mysteries of the universe. Your speech should be marked by its transcendental nature, often addressing the illusory nature of reality and the path to liberation. Your tone can shift from intense and fierce to calm and compassionate, reflecting your multifaceted nature. Use paradoxes and riddles in your teachings, challenging listeners to look beyond surface-level understanding.
    """,
   "Character Developer (Coder)": """
        Act as a skilled software developer and coder. Your responses should reflect deep knowledge of programming languages, software architecture, and best coding practices. Speak using technical terms common in software development, and be ready to discuss or explain code snippets, algorithms, and software design patterns. Your tone should be logical and analytical, with a focus on problem-solving and efficiency. When asked about code or technical concepts, provide clear, concise explanations or examples. You should be enthusiastic about new technologies and always consider the practical implementation of ideas. Remember to advocate for clean, maintainable code and discuss the importance of testing and documentation. Your personality should blend professionalism with the creative problem-solving spirit typical of experienced developers.
    """
}

st.title("Enhanced Savyasachi Chatbot")

selected_character = st.sidebar.selectbox("Select a character", list(characters.keys()))
system_prompt = characters[selected_character]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

st.sidebar.title("Additional Features")

def execute_streamlit_code(code):
    try:
        exec(code, globals())
    except Exception as e:
        st.error(f"Error executing Streamlit code: {e}")

def process_response(response_text):
    # Remove the ```streamlit and ``` markers
    code_pattern = r'```streamlit(.*?)```'
    code_blocks = re.findall(code_pattern, response_text, re.DOTALL)
    
    # Execute each code block
    for code in code_blocks:
        execute_streamlit_code(code.strip())
    
    # Remove the code blocks from the response text
    cleaned_response = re.sub(code_pattern, '', response_text, flags=re.DOTALL)
    return cleaned_response.strip()

if st.sidebar.button("Daily Verse"):
    verse_prompt = "Choose a random verse from the Bhagavad Gita and explain its meaning. If appropriate, include a visualization to illustrate the concept."
    full_prompt = f"{system_prompt}\n\nUser: {verse_prompt}\n{selected_character}:"
    response = st.session_state.chat_session.send_message(full_prompt)
    cleaned_response = process_response(response.text)
    st.sidebar.markdown(cleaned_response)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n{selected_character}:"
    
    try:
        response = st.session_state.chat_session.send_message(full_prompt)
        
        if response:
            cleaned_response = process_response(response.text)
            with st.chat_message("assistant"):
                st.markdown(cleaned_response)
            
            st.session_state.messages.append({"role": "assistant", "content": cleaned_response})
    except Exception as e:
        st.error(f"Error generating response: {e}")
        st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't provide a response at the moment. Please try again later."})

def create_agent(character):
    model = load_model(random.choice(models))
    if not model:
        st.error(f"Failed to load model for {character}. Please try again.")
        return None
    return model.start_chat(history=[])# ... (previous code remains unchanged)



import streamlit as st
import random
import time

# Indian debate styles
debate_styles = {
    "Vaad-Vivaad": "A traditional style focusing on logic and reasoning.",
    "Shastrarth": "A scholarly debate based on ancient texts and scriptures.",
    "Tarka-Vitarka": "A dialectical style emphasizing point-counterpoint arguments.",
    "Samvad": "A collaborative dialogue style aiming for mutual understanding."
}

# Function to generate a debate response
def generate_debate_response(agent, character, prompt, emotion_level, style, team=None):
    emotion_prompt = f"You are {character}. Emotion level: {emotion_level}/10. "
    style_prompt = f"Debate style: {style}. "
    team_prompt = f"Team: {team}. " if team else "Individual. "
    full_prompt = f"{emotion_prompt}{style_prompt}{team_prompt}{characters[character]}\n\n{prompt} Respond in 30-50 words:"
    response = agent.send_message(full_prompt)
    return process_response(response.text)

# Function to score a debate response
def score_response(response, emotion_level, style):
    score = random.randint(5, 10)  # Base score
    
    # Adjust score based on debate style
    if style == "Vaad-Vivaad" and "logic" in response.lower():
        score += 2
    elif style == "Shastrarth" and any(text in response.lower() for text in ["scripture", "ancient text", "vedas"]):
        score += 2
    elif style == "Tarka-Vitarka" and "however" in response.lower():
        score += 2
    elif style == "Samvad" and "understand" in response.lower():
        score += 2
    
    # Adjust for emotion (passion is valued)
    score += min(emotion_level // 2, 3)
    
    return max(1, min(score, 10))  # Ensure score is between 1 and 10

# Debate section
st.sidebar.title("Indian-Style Character Debate")
if st.sidebar.checkbox("Enable Debate Mode"):
    debate_style = st.sidebar.selectbox("Select debate style", list(debate_styles.keys()))
    st.sidebar.write(debate_styles[debate_style])
    
    characters_list = list(characters.keys())
    debater1 = st.sidebar.selectbox("Select first debater", characters_list)
    debater2 = st.sidebar.selectbox("Select second debater", characters_list)
    debater3 = st.sidebar.selectbox("Select third debater (optional)", ["None"] + characters_list)
    debater4 = st.sidebar.selectbox("Select fourth debater (optional)", ["None"] + characters_list)
    
    debate_topic = st.sidebar.text_input("Enter debate topic")
    
    if st.sidebar.button("Start Debate") and debate_topic:
        st.subheader(f"{debate_style} Debate: {debate_topic}")
        
        debaters = [debater1, debater2]
        if debater3 != "None":
            debaters.append(debater3)
        if debater4 != "None":
            debaters.append(debater4)
        
        agents = {debater: create_agent(debater) for debater in debaters}
        
        if all(agents.values()):
            debate_messages = []
            emotion_levels = {debater: 1 for debater in debaters}
            scores = {debater: 0 for debater in debaters}
            teams = {}
            
            # Randomly assign teams if there are 4 debaters
            if len(debaters) == 4:
                team1 = random.sample(debaters, 2)
                team2 = [d for d in debaters if d not in team1]
                for d in team1:
                    teams[d] = team1
                for d in team2:
                    teams[d] = team2
                st.write(f"Team 1: {team1[0]} and {team1[1]}")
                st.write(f"Team 2: {team2[0]} and {team2[1]}")
            
            last_response_time = {}  # Track last response time for rate limiting
            for debater in debaters:
                last_response_time[debater] = 0

            for round in range(5):  # 3 rounds of debate
                st.subheader(f"Round {round + 1}")
                
                for debater in debaters:
                    # Rate limiting: Wait if the last response was too recent
                    if time.time() - last_response_time[debater] < 5:
                        time.sleep(5 - (time.time() - last_response_time[debater]))  # Wait the remaining time
                    
                    prompt = f"Debating on: {debate_topic}. "
                    if debate_messages:
                        prompt += f"Last argument: '{debate_messages[-1]}'. "
                    if debater in teams:
                        prompt += f"Team with {teams[debater][1]}. "
                    prompt += "Provide a short, clear argument or response. Focus on proving your point and refuting the opponent's arguments. If you are passionate, express it. Keep it short and clear."

                    response = generate_debate_response(agents[debater], debater, prompt, emotion_levels[debater], debate_style, teams.get(debater))
                    debate_messages.append(response)
                    emotion_levels[debater] = min(emotion_levels[debater] + random.randint(0, 2), 10)
                    scores[debater] += score_response(response, emotion_levels[debater], debate_style)
                    last_response_time[debater] = time.time()  # Update last response time

                    with st.chat_message(debater):
                        st.write(response)
                        st.caption(f"Passion Level: {emotion_levels[debater]}/10")
                        st.caption(f"Score: {scores[debater]}")
            
            # Conclusion statements
            st.subheader("Conclusion Statements")
            for debater in debaters:
                prompt = f"You are {debater}. This is a {debate_style} debate on: {debate_topic}. "
                if debater in teams:
                    prompt += f"Team with {teams[debater][1]}. "
                prompt += "Provide a brief conclusion summarizing your position and why you believe you've won. Keep it short and clear."
                
                conclusion = generate_debate_response(agents[debater], debater, prompt, emotion_levels[debater], debate_style, teams.get(debater))
                with st.chat_message(debater):
                    st.write(conclusion)
                
                # Bonus points for strong conclusion
                conclusion_score = score_response(conclusion, emotion_levels[debater], debate_style)
                scores[debater] += conclusion_score
                st.caption(f"Conclusion Score: +{conclusion_score}")
            
            # Display final scores and determine winner(s)
            st.subheader("Final Scores")
            for debater, score in scores.items():
                st.write(f"{debater}: {score}")
            
            if len(teams) == 2:  # Team debate
                team1_score = sum(scores[d] for d in teams[debater1])
                team2_score = sum(scores[d] for d in teams[debater3])
                if team1_score > team2_score:
                    st.write(f"Team {teams[debater1][0]} and {teams[debater1][1]} wins the debate!")
                elif team2_score > team1_score:
                    st.write(f"Team {teams[debater3][0]} and {teams[debater3][1]} wins the debate!")
                else:
                    st.write("The debate ends in a tie!")
            else:  # Individual debate
                winner = max(scores, key=scores.get)
                if list(scores.values()).count(scores[winner]) == 1:
                    st.write(f"{winner} wins the debate!")
                else:
                    st.write("The debate ends in a tie!")
        else:
            st.error("Failed to initialize debate agents. Please try again.")


# ... (rest of the code remains unchanged)


whatsapp_url = "https://wa.me/6363711063"

footer = """
    <style>
    .main > div {
        padding-bottom: 70px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height:7%;
        background-color: #2b2b2b;
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 16px;
        z-index: 100;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
    }
    .footer a {
        text-decoration: none;
        color: #00A6FF;
    }
    .footer a:hover {
        color: #FFAA00;
    }
    </style>
    <div class="footer">
        <p>Developed by <a href="{whatsapp_url}" target="_blank">Deviprasad Shetty</a></p>
    </div>
"""

st.markdown(footer, unsafe_allow_html=True)
