# import pandas as pd
import os
import base64  # to enable writing to GitHub repo
import requests  # ditto
from datetime import datetime

# My GitHub info
token = "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"
repo = "JulienHartley/KiuzTuB-project"
branch = "main"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# Set the folder path where the CSV files are located
folder_path = "Results/"
number_of_files = 0
# Get all filenames for files in the folder that start with "response"
csv_files = [f for f in os.listdir(folder_path) if f.startswith("response")]
# print(csv_files)
new_file_content = ""
# Loop through each CSV file and read it and append its content to the consolidated_results content
for file in csv_files:
    file_path = os.path.join(folder_path, file)
#    print("file path:", file_path)

#   input_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
#   response = requests.get(input_url, headers=headers)
#   content_data = response.text
#   decode the line content
#   line_content = base64.b64decode(content_data).decode()

    # get the content from the file
    with open(file_path, "r", encoding="utf-8") as in_f:
        content_data = in_f.readline()

#   print("content data:", content_data)

# === Add this line to the output (existing_content) ===
    new_file_content = new_file_content + content_data + "\n"
    number_of_files = number_of_files + 1
#   print(new_file_content)

# now encode the new file content for writing to the output file
encoded_content = base64.b64encode(new_file_content.encode()).decode()

# === Create api url for the consolidated results file
filename = "Results/" + f"Consolidated_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"

data = {
    "message": f"Add {filename}",
    "content": encoded_content,
    "branch": branch
}
# put the content (data) into the file
response = requests.put(api_url, headers=headers, json=data)

if response.status_code == 201:
    print(f"File containing {number_of_files} lines created successfully!")
else:
    print(f"Error: {response.status_code} - {response.json()}")
