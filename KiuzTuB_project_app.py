import streamlit as st
# import pandas as pd
import os
import base64  # to enable writing to GitHub repo
import requests  # ditto
import random

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
        
        You’ll view five panels from a comic.
        
        After seeing them you will be asked what you think happens next,
        how confident you are in your answer, and what clues you used (these may be textual or visual).
        
        All responses are anonymous.  
        """)
        st.session_state.proceed = st.form_submit_button("Continue")
        if not st.session_state.proceed:
            st.stop()

# === This section determines which item this participant will see
if "final_images" not in st.session_state:
#    st.write("""reached the loading of the items""")
    #  first choose two items from the first 5 (the original comics)
    item1 = random.randint(1, 5)  # includes both 1 and 5
    item3 = item1
    while item3 == item1:  # keep generating a random number until it is different from item1
        item3 = random.randint(1, 5)
#    st.write(f"The original items for this participant are {item1} and {item3}")

    #  now choose two items from the second 5 (the created comics)
    item2 = random.randint(6, 10)  # includes both 6 and 10
    item4 = item2
    while item4 == item2:  # keep generating a random number until it is different from item2
        item4 = random.randint(6, 10)
#    st.write(f"The created items for this participant are {item2} and {item4}")

    item1_panels = [f"panels{item1}.png"]
    item2_panels = [f"panels{item2}.png"]
    item3_panels = [f"panels{item3}.png"]
    item4_panels = [f"panels{item4}.png"]

    st.session_state.final_images = item1_panels + item2_panels + item3_panels + item4_panels

# === Now Loop through the items, presenting the panels and questions for each
# Initialize index in session state to -1, so that next time through it increments to 0
if "item_index" not in st.session_state:
    st.session_state.item_index = -1

# Show each item and its questions in turn
if "item_index" in st.session_state:
    st.session_state.item_index += 1
    item_number_str = str(st.session_state.item_index)
#    st.write(f"The item index is {st.session_state.item_index} ({item_number_str})")

    if st.session_state.item_index < 4:
        with st.form(f"item_{item_number_str}"):
            current_item = st.session_state.final_images[st.session_state.item_index]
    #        st.write(f"The image to be shown is {current_item}")

            st.image(os.path.join("Images", current_item))
#            next_item = st.form_submit_button("Next")
#           if not next_item:
#               st.stop()
#           else:  # ask the questions that relate to the item
#               if "answer{item_index}" not in st.session_state:
#                   with st.form("response_form"):
            st.write("""
            
            ### Please type your responses to the questions below ###
            
            """)
            answer = st.text_input("What do you think happens next?", key=f"answer{item_number_str}")
#            submit = st.form_submit_button("Submit")
#                       if not submit:
#                           st.stop()
#
#               if "confidence{item_index}" not in st.session_state:
#                   with st.form("confidence_form"):
            st.write("""
            
            """)
            confidence = st.selectbox(
                "How confident do you feel about this on a scale of 1(low) to 10(certain)?",
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], key=f"confidence{item_number_str}")
#                        submit = st.form_submit_button("Submit")
#                       if not submit:
#                           st.stop()

#               if "clues{item_index}" not in st.session_state:
#                   with st.form("clues form"):
            st.write("""
     
            """)
            clues = st.text_input("What clues (if any) did you use to reach your prediction? (enter up to 3)",
                                  key=f"clues{item_number_str}")
            submit = st.form_submit_button("Submit")
            if not submit:
                st.stop()


# === This section writes the participant record to the GitHub file
if "clues3" in st.session_state:

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
                    st.session_state.answer0,
                    str(st.session_state.confidence0),
                    st.session_state.clues0,
                    st.session_state.answer1,
                    str(st.session_state.confidence1),
                    st.session_state.clues1,
                    st.session_state.answer2,
                    str(st.session_state.confidence2),
                    st.session_state.clues2,
                    st.session_state.answer3,
                    str(st.session_state.confidence3),
                    st.session_state.clues3
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
