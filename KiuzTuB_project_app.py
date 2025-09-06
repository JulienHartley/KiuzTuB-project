import streamlit as st
# import pandas as pd
import os
import base64  # to enable writing to GitHub repo
import requests  # ditto

from datetime import datetime

st.set_page_config(page_title="Comic Panel Experiment", layout="centered")
st.title("🧠 Comic Panel Experiment")

# === Participant Info Form ===
if "age" not in st.session_state:
    with st.form("participant_form"):
        st.write("### Please tell us about yourself")
        gender = st.selectbox("Gender:", ["Prefer not to say", "Female", "Male", "Other"], key="gender")
        age = st.text_input("Your age:", key="age")
        submit = st.form_submit_button(label="Start")
        if not submit:
            st.stop()

# === assign participant number - this will be one more than the number in Participant.txt
if "participant" not in st.session_state:
    participant_file = "Participant.txt"
    with open(participant_file, "r", encoding="utf-8") as in_f:
        try:
            participant = int(in_f.readline()) + 1
        except ValueError:
            participant = 1
    st.session_state.participant = participant

# === Now update the Participant.txt file with the number of this participant
    output_record = str(participant)
    encoded_content = base64.b64encode(output_record.encode("utf-8")).decode("utf-8")

    # My GitHub info
    # Get GitHub token from secrets
    github_token = st.secrets["GITHUB_TOKEN"]
    repo = "JulienHartley/KiuzTuB-project"
    branch = "main"

    api_url = f"https://api.github.com/repos/{repo}/contents/{participant_file}"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info["sha"]
    else:
        st.error(f"Failed to fetch file info: {response.status_code}")
        st.stop()

    update_payload = {
        "message": f"Update file via Streamlit {st.session_state.participant}",
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    # write the update request
    update_response = requests.put(api_url, headers=headers, json=update_payload)
    if update_response.status_code == 200:
        st.success("✅ File updated successfully!")
    else:
        st.error(f"❌ Update failed: {update_response.status_code}")
        st.json(update_response.json())

    st.success(f"🧪 You are participant **{participant}**.")

# === This section handles the instructions screen
if "proceed" not in st.session_state:
    with st.form("instructions_form"):
        st.write("""
        Welcome to our experiment!
        
        The purpose of the experiment is to compare human prediction in comics with the prediction of an AI Chatbot
        
        You’ll view a (small) number of panels from a comic.
        
        After seeing them you will be asked what you think happens next,
        how confident you are in your answer, and what clues you used (these may be textual or visual).
        
        All responses are anonymous.  
        """)
        st.session_state.proceed = st.form_submit_button("Continue")
        if not st.session_state.proceed:
            st.stop()

# === This section determines which of the 5 items this participant will see; this will be determined using base 5
# === eg, participant 1 gets item 1, participant 9 gets item 5, etc

# === Read the list of comic names and panel numbers and store them in a session_state variable
if "cartoons" not in st.session_state:
    cartoons_file = "Cartoon_list.txt"
    st.session_state.cartoons = []
    with open(cartoons_file, "r", encoding="utf-8") as in_f:
        for line in in_f:
            cartoon_name, cartoon_panels = line.strip().split(",")  # split into 2 parts
            st.session_state.cartoons.append((cartoon_name, int(cartoon_panels)))   # store as (string, int)

# === if the images for this participant have not yet been loaded, select the cartoon based on the participant number
# === and load the images into a session_state variable (final_images)
if "final_images" not in st.session_state:
    st.session_state.item = (st.session_state.participant % 5) - 1
    panel_no = 1
    st.session_state.final_images = []
    while panel_no < (st.session_state.cartoons[st.session_state.item][1] + 1):
        st.session_state.final_images = (st.session_state.final_images +
                                         [f"{st.session_state.cartoons[st.session_state.item][0]}_{panel_no}.png"])
        panel_no += 1

# === Now Loop through the panels
# Initialize index in session state to -1; thereafter each time through it increments by 1
if "panel_index" not in st.session_state:
    st.session_state.panel_index = -1

# Increment the panel number by 1 and then show the panels (Note that the array index goes from 0 to 5)
if "panel_index" in st.session_state:
    st.session_state.panel_index += 1
    panel_number_str = str(st.session_state.panel_index)

    # As long as panel_index is less the number of panels in the item, show the (next) panel
    if st.session_state.panel_index < st.session_state.cartoons[st.session_state.item][1] - 1:
        with st.form(f"item_{panel_number_str}"):
            current_panel = st.session_state.final_images[st.session_state.panel_index]
            st.image(os.path.join("Images", current_panel))
            next_item = st.form_submit_button("Next")
            if not next_item:
                st.stop()

    # Now elicit the answers to the questions
    with st.form("questions_form"):
        st.write("""
                
                ### Please type your responses to the questions below ###
                
                """)

        st.session_state.answer = st.text_input("What do you think happens next?")
        st.write("""
                
                """)

        st.session_state.confidence = st.selectbox(
                    "How confident do you feel about this on a scale of 1(low) to 10(certain)?",
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

        st.write("""
         
                """)

        st.session_state.clues = st.text_input(
            "What clues (if any) did you use to reach your prediction? (enter up to 3 separated by ,)")

        submit = st.form_submit_button("Submit")
        if not submit:
            st.stop()


# === This section writes the participant record to the GitHub file
if "clues" in st.session_state:

    # My GitHub info
    github_token = st.secrets["GITHUB_TOKEN"]
    repo = "JulienHartley/KiuzTuB-project"
    branch = "main"

    # === Save CSV
    filename = "Results/" + f"response_{st.session_state.participant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    output_array = [str(st.session_state.participant),
                    str(st.session_state.age),
                    st.session_state.gender,
                    st.session_state.cartoons[st.session_state.item][0],
                    st.session_state.answer,
                    str(st.session_state.confidence),
                    st.session_state.clues
                    ]
    # st.write(f"The output record is {output_array}")
    output_record = ",".join(output_array)
    encoded_content = base64.b64encode(output_record.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Add {filename}",
        "content": encoded_content,
        "branch": branch
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 201:
        st.success("File created successfully!")
    else:
        st.error(f"Error: {response.status_code} - {response.json()}")


st.success("✅ Thank you! Your responses have been recorded. You may close this browser window")
