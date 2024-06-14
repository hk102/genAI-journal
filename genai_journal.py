import streamlit as st
import requests
import json
from groq import Groq
from gtts import gTTS
import io
import base64
import random
import matplotlib.pyplot as plt
import pandas as pd
from openai import OpenAI, AzureOpenAI



# client = Groq(
#     api_key=st.secrets["GROQ_KEY"],
# )

client = OpenAI(api_key = st.secrets["OPEANAI_KEY"])

with open("qna_bank.json","r") as file:
    question_bank = json.load(file)

# Initialize session state for questions
if "questions" not in st.session_state:
    q_index = random.randint(0, len(question_bank) - 1)
    st.session_state.questions = question_bank[q_index]

questions = st.session_state.questions

# Function to simulate data storage
def store_responses(question_index, user_response, free_text):
    if "responses" not in st.session_state:
        st.session_state["responses"] = []
    # Check if the response for this question index is already stored and update it if needed
    response_found = False
    for i, (idx, _, _) in enumerate(st.session_state["responses"]):
        if idx == question_index:
            st.session_state["responses"][i] = (question_index, user_response, free_text)
            response_found = True
            break
    # If response not found, add it
    if not response_found:
        st.session_state["responses"].append((question_index, user_response, free_text))

# Function to generate script
def generate_script(qna_pairs):
    qna_pairs_string = json.dumps(qna_pairs)
    query = """
    below are the few details for user's that day's activity, so please create it super creative & uniqe 30-60 seconds script , it should only contains text which user can directly read & speak. Or with bot can directly convert from text to speech. Don't add anything except script in output. User is going to do voice over with this, so use I instead of You.

    QnA:

    %s

    output formate:

    {
        "script" : <script>
    }


    """ % (qna_pairs_string)

    # chat_completion = client.chat.completions.create(
    #                                                 messages=[
    #                                                     {
    #                                                         "role": "user",
    #                                                         "content": query,
    #                                                     }
    #                                                 ],
    #                                                 model="llama3-8b-8192",
    #                                             )

    # script = chat_completion.choices[0].message.content
    # script = script.split('"')[1]

    
    response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query},
                
            ]
            )
    script =  json.loads(response.choices[0].message.content)
    script = script["script"]
    
    return script

# Function to simulate text-to-audio conversion
def text_to_audio(script):
    # Simulate text-to-audio conversion
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save("day1.mp3")


def genai_result(prompt):

    response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                
            ]
            )
    return response.choices[0].message.content






# Initialize session state
if "responses" not in st.session_state:
    st.session_state["responses"] = []
if "current_question" not in st.session_state:
    st.session_state["current_question"] = 0

# Left Panel with sections
st.sidebar.title("GenAI Journal")

# Section selection
selected_section = st.sidebar.radio("Select a Section", ["Intro","Question - Answering", "Script generation", "Convert Script to Audio", "Create Video", "Report"])

# Initialize the session state for the button label
if "script_button_label" not in st.session_state:
    st.session_state.script_button_label = "Generate Script"

# Initialize the session state for the generated script
if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""


# Section 1: Intro
if selected_section == "Intro":
    st.sidebar.header("1. Intro")

    
    st.header("Welcome to the GenAI Journal!")
    st.write("""
    * Revolutionize your journaling experience with cutting-edge AI technology
 * Engage in daily conversations with a thoughtful AI assistant about your day
* Receive a personalized multimedia journal entry in video format, complete with audio and visuals
* Gain valuable insights into your productivity levels and track your progress over time
* Discover tools and guidance to help you unlock your ikigai (life's purpose)
* Option for personalized mentorship to stay motivated and achieve your goals
    """)
    if st.button("Get Started"):
        selected_section = "Question - Answering"

        
    


# Section 1: Question - Answering
elif selected_section == "Question - Answering":
    st.sidebar.header("2. Question - Answering")

    # Display current question
    def display_question(question_index):
        question = questions[question_index]
        st.subheader(question["question"])

        # Check if there's already a stored response for this question index
        stored_response = next((response for idx, response, _ in st.session_state["responses"] if idx == question_index), None)
        default_index = question["options"].index(stored_response) if stored_response in question["options"] else 0

        user_response = st.radio("", question["options"], index=default_index, key=f"question_{question_index}")

        st.subheader("Any explanation or additional input?")
        # Check if there's already a stored free text response for this question index
        stored_text = next((text for idx, _, text in st.session_state["responses"] if idx == question_index), "")

        free_text = st.text_area("", value=stored_text, key=f"text_{question_index}", height=30)

        # Store responses immediately
        store_responses(question_index, user_response, free_text)

        return user_response, free_text

    if "responses" in st.session_state and st.session_state["responses"]:
        qna_pair = []
        for question_index, response, text in st.session_state["responses"]:
            temp = {"questions" : questions[question_index]["question"],
                        "answer" : response,
                        "extra_inputs" : text }
            qna_pair.append(temp)

        json_string = json.dumps(qna_pair)


    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.session_state["current_question"] > 0:
            if st.button("Previous"):
                st.session_state["current_question"] -= 1

    with col3:
        if st.session_state["current_question"] < len(questions) - 1:
            if st.button("Next"):
                st.session_state["current_question"] += 1

    with col2:
        if st.session_state["current_question"] == len(questions) - 1:
            # st.download_button(
            #                          label="Download JSON",
            #                         file_name="data.json",
            #                         mime="application/json",
            #                         data=json_string,
            #                     )
            if st.button("Submit"):
                st.session_state["current_question"] += 1
                st.text(json_string)

    # Display current question
    if st.session_state["current_question"] < len(questions):
        current_question_index = st.session_state["current_question"]
        display_question(current_question_index)
    else:
        st.subheader("Thank you for answering all the questions!")

# Section 2: Script generation from previously answered questions
elif selected_section == "Script generation":
    st.sidebar.header("4. Script generation from previously answered questions")

    if st.button(st.session_state.script_button_label):

        if "responses" in st.session_state and st.session_state["responses"]:
            qna_pair = []
            for question_index, response, text in st.session_state["responses"]:
                temp = {"questions" : questions[question_index]["question"],
                            "answer" : response,
                            "extra_inputs" : text }
                qna_pair.append(temp)
            
            st.subheader("Generated Script:")
            script = generate_script(qna_pair)
            st.write(script)
            st.session_state.generated_script = script
            st.session_state.script_button_label = "Re-generate Script"
        else:
            st.write("Answer some questions to generate the script.")

# Section 3: Convert Script to Audio
elif selected_section == "Convert Script to Audio":
    st.sidebar.header("5. Convert Script to Audio")

    if st.session_state["responses"] and st.session_state.generated_script :
        if st.button("Convert Script to Audio"):
            audio_content = text_to_audio(st.session_state.generated_script)
            st.audio("day1.mp3")
    else:
        st.write("Answer some questions to generate the script and convert it to audio.")

# Section 4: Create Video from Audio & lip sync api
elif selected_section == "Create Video":
    st.sidebar.header("6. Create Video from Audio & lip sync api")

    if st.session_state["responses"]:
        # if st.button("Create Video"):
        #     #  video creation
        #     pass
        # Define a list of avatar video options
        avatar_videos = {
            "Avatar 1": "./avatar_video/avatar1.mp4",
            "Avatar 2": "./avatar_video/avatar2.mp4",
            "Avatar 3": "./avatar_video/avatar3.mp4",
            "Avatar 4": "./avatar_video/avatar4.mp4",
            # "Avatar 5": "avatar5.mp4"
        }

        # Create two columns
        col1, col2 = st.columns(2)

        # Display the select box in the first column
        with col1:
            selected_avatar = st.selectbox("Select an Avatar", list(avatar_videos.keys()), index=0)

        # Display the avatar video in the second column
        with col2:
            pass


    else:
        st.write("Answer some questions to generate the script and create the video.")

# Section 4: Create Report
elif selected_section == "Report":
    st.sidebar.header("7. Create Report")

    if "responses" in st.session_state and st.session_state["responses"]:
        qna_pair = []
        for question_index, response, text in st.session_state["responses"]:
            temp = {"questions" : questions[question_index]["question"],
                        "answer" : response,
                        "extra_inputs" : text }
            qna_pair.append(temp)

        json_string = json.dumps(qna_pair)

    if st.session_state["responses"]:
        if st.button("Create Report"):
            def calculate_ikigai_score(passion, mission, profession, vocation):
                return passion + mission + profession + vocation

            def display_ikigai_score(score):
                st.subheader(f"Your Ikigai Score: {score}")
                
                # Create a data frame for the pie chart
                data = pd.DataFrame({'Category': ['Passion', 'Mission', 'Profession', 'Vocation'],
                                    'Score': [passion, mission, profession, vocation]})
                
                # Create the pie chart
                fig, ax = plt.subplots()
                ax.pie(data['Score'], labels=data['Category'], autopct='%1.1f%%')
                ax.axis('equal')  # Ensure the pie chart is circular
                
                # Display the pie chart in Streamlit
                st.pyplot(fig)

            # Streamlit app
            st.title("Ikigai Scoring")

            # Prompt for Report Score
            qna = json_string
            prompt = """
Below are the qna collected from user for his daily activity. 

QnA:

%s

---------------------------------------------------------------

Want results in below json form. just need overall score not for each individual question. And share only json form result nothing else in result. All score is out of 10.
 

{
'Passion' : <passion score>,
'Mission' : <mission score>,
'Profession' : <profession score>,
'Vocation': <vocation score>
}


""" %(qna)

            # Genai Result
            report_result = genai_result(prompt)
            prompt = f""" Please give only json result only from below text \n\n {report_result}"""
            report_result = json.loads(genai_result(prompt))

            # Get user inputs
            passion = st.slider("Passion", 0, 10, int(report_result["Passion"]))
            mission = st.slider("Mission", 0, 10, int(report_result["Mission"]))
            profession = st.slider("Profession", 0, 10, int(report_result["Profession"]))
            vocation = st.slider("Vocation", 0, 10, int(report_result["Vocation"]))

            # Calculate Ikigai score
            ikigai_score = calculate_ikigai_score(passion, mission, profession, vocation)

            # Display Ikigai score and pie chart
            display_ikigai_score(ikigai_score)

            with st.expander("Actionable Steps for Tomorrow:"):
                qna = json_string
                tomorrow_prompt = f"""
Below are the qna collected from user for his daily activity. 

QnA:

{qna}

---------------------------------------------


Please I am trying to achieve ikigai, so please help provide a way what can I do better tomorrow from my today's routine. Instead of giving generlize answer give some specific & personalize answer. I need few points 4-5 catagories, : 

Give me only results in some catagories without adding any extra text.

output formate:


1. catagory1:
  - <suggestion>
  - <suggestion>
  .
  .

2. catagory2:
.
.
.
.
.


"""
                actionable_steps_for_tomorrow = genai_result(tomorrow_prompt)
                st.write(actionable_steps_for_tomorrow)


    else:
        st.write("Answer some questions to generate the script and create the video.")

