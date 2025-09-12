# import pandas as pd
import os
# import streamlit as st
# import base64  # to enable writing to GitHub repo
# import requests  # ditto
from datetime import datetime


# Set the folder path where the CSV files are located
folder_path = "Results/"
number_of_files = 0
# === create filename for the consolidated results file
filename = "Results/" + f"Consolidated_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Get all filenames for files in the folder that start with "response"
csv_files = [f for f in os.listdir(folder_path) if f.startswith("response")]
csv_files.sort()

# write the headers line for the csv file
with open(filename, "w") as out_f:
    out_f.write(
        "Participant," +
        "Age," +
        "Gender," +
        "Cartoon," +
        "Prediction," +
        "confidence level," +
        "Clue 1," +
        "Clue 2," +
        "Clue 3," +
        "\n")
# Loop through each CSV file and read it and append its content to the consolidated results file
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    print("file path:", file_path)

    # get the content from the file
    with open(file_path, "r", encoding="utf-8") as in_f:
        content_data = in_f.readline()

    print("content data:", content_data)

# === Add this line to the output (existing_content) ===
    with open(filename, "a") as out_f:
        out_f.write(content_data + "\n")

    number_of_files = number_of_files + 1
