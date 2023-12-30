import uuid

import streamlit as st
from openai import OpenAI

from trubrics.integrations.streamlit import FeedbackCollector

college_board_logo = "https://wthsscratchpaper.net/wp-content/uploads/2023/03/College-Board-Logo-Icon.jpg"
codee_avatar = 'https://miro.medium.com/v2/resize:fit:525/1*lyyXmbeoK5JiIBNCnzzjjg.png'

st.set_page_config(
    page_title="Codee-B",
    page_icon=college_board_logo,
    layout="wide",
)

st.title("Codee-B")

with st.expander("ℹ️ Disclaimer"):
    st.caption(
        f"""We appreciate your engagement! Please note, this is research purposes only. 
        Thank you for your understanding. Be sure to add this to the survey.
        """
    )
    
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    # Create a user_id for the session
    user_id = st.text_input("Participant #", key="user_id", type="password")

collector = FeedbackCollector(
    project="codee_b",
    email=st.secrets["TRUBRICS_EMAIL"], 
    password=st.secrets["TRUBRICS_PW"]
)

count = 0  # Needed for unique Streamlit keys

# Initialize chat history
if "messages" not in st.session_state:
    # Start with first message from assistant
    st.session_state['messages'] = [{"role": "assistant", 
                                  "content": f"Hi student! I'm Codee-B, an intelligent AI for Computer Science Principles. How can I help you today?"}]

# Trubrics info
if "prompt_ids" not in st.session_state:
    st.session_state["prompt_ids"] = []

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    
tags = [f"llm_chatbot_stream.py"]

# GPT info
model = "gpt-4"

temperature = 0.3

messages = st.session_state.messages

# Display messages and feedback mechanism
for n, msg in enumerate(st.session_state.messages):
    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar=codee_avatar).markdown(msg["content"])
    else:
        st.chat_message(msg["role"]).markdown(msg["content"])

    if msg["role"] == "assistant" and n > 1:
        feedback_key = f"feedback_{int(n / 2)}"

        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None

        # In-app feedback container
        with st.container(border=True):
            col1, col2 = st.columns(2)
        
            with col1:
                st.markdown(f"How well do you believe that the chatbot answered your question?")
                st.markdown(f"How well did the agent's response take into account your personal background and experience?")
                st.markdown(f"How understandable do you believe the agent's response was to you?")
                st.markdown(f"If there are examples shown to you, how understandable do you believe the examples were to you?")
            
            with col2:        
                feedback1 = collector.st_feedback(
                    component="q1",
                    feedback_type="faces",
                    model=model,
                    # open_feedback_label="[Optional] Provide additional feedback",  # For optional open-ended feedback
                    prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
                    user_id=user_id,
                    key="q1-" + str(count),
                )
                
                feedback2 = collector.st_feedback(
                    component="q2",
                    feedback_type="faces",
                    model=model,
                    # open_feedback_label="[Optional] Provide additional feedback",  # For optional open-ended feedback            
                    prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
                    user_id=user_id,
                    key="q2-"+  str(count),
                )
                
                feedback3 = collector.st_feedback(
                    component="q3",
                    feedback_type="faces",
                    model=model,
                    # open_feedback_label="[Optional] Provide additional feedback",  # For optional open-ended feedback
                    prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
                    user_id=user_id,
                    key="q3-"+  str(count),
                )
                
                feedback4 = collector.st_feedback(
                    component="q4",
                    feedback_type="faces",
                    model=model,
                    # open_feedback_label="[Optional] Provide additional feedback",  # For optional open-ended feedback
                    prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
                    user_id=user_id,
                    key="q4-"+  str(count),
                )

        count += 1  # Increment count for unique streamlit component keys
        
        # Debug-mode below - Uncomment below to see the feedback sent to TRubrics

        # if feedback1:
        #     with st.sidebar:
        #         st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
        #         st.write(feedback1)
        # if feedback2:
        #     with st.sidebar:
        #         st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
        #         st.write(feedback2)
        # if feedback3:
        #     with st.sidebar:
        #         st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
        #         st.write(feedback3)
        # if feedback4:
        #     with st.sidebar:
        #         st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
        #         st.write(feedback4)

# Chat input
if prompt := st.chat_input("Let's chat"):
    # Verify input
    if not openai_api_key or openai_api_key != st.secrets["OPENAI_API_KEY_B"]:
        st.info("Please add/update your OpenAI API key to continue.")
        st.stop()
    else:
        client = OpenAI(api_key=openai_api_key)
        
    if not user_id:
        st.info("Please add your Participant # to continue.")
        st.stop()

    st.session_state...append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant", avatar=codee_avatar):
        message_placeholder = st.empty()
        generation = ""
        
        for part in client.chat.completions.create(
            model=model,
            messages=messages, 
            temperature=temperature,
            stream=True
        ):
            generation += part.choices[0].delta.content or ""
            message_placeholder.markdown(generation + "▌")
        message_placeholder.markdown(generation)

        logged_prompt = collector.log_prompt(
            config_model={"model": model},
            prompt=prompt,
            generation=generation,
            session_id=st.session_state['session_id'],
            tags=tags,
            user_id=user_id,
        )
        st.session_state.prompt_ids.append(logged_prompt.id)
        st.session_state.messages.append({"role": "assistant", "content": generation})
        st.rerun() 
                