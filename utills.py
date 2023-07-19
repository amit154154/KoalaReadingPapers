import sys
import PyPDF2
import requests
from glob import glob
from elevenlabs import clone, generate, play, set_api_key,save
from elevenlabs.api import History
import os
import audioread
from pydub import AudioSegment

elevenlabs_api_key = ''
chatpdf_api = ''

def upload_paper(paper_path):
    files = [
    ('file', ('file', open(paper_path, 'rb'), 'application/octet-stream'))
    ]
    headers = {
        'x-api-key': chatpdf_api,
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

    if response.status_code == 200:
        return response.json()['sourceId']
    else:
        return None

def ask_paper(paper_api_key,content):
    headers = {
        'x-api-key': chatpdf_api, ##api code
        "Content-Type": "application/json",
    }

    data = {
        'sourceId': f"cha_{paper_api_key}",
        'messages': [
            {
                'role': "user",
                'content': content
            }
        ]
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['content']
    else:
        return None
def extract_text_from_pdf(file_path):
    with open(file_path,'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text =''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

def create_overview(pdf_dir_path,overview_tamplate_path,papers_api):
    overview_text = ''
    with open(overview_tamplate_path, 'r') as file:
        overview_text += file.read() + '\n'

    pdfs_path = glob(f'{pdf_dir_path}/*.pdf')
    pdfs_titles = [extract_text_from_pdf(i).split('\n')[0] for i in pdfs_path]

    chat_text = 'summarize the paper in one short line, it should have also the results they go'
    print('getting overview of the papers')
    papers_quickoverview = [ask_paper(p_api,chat_text) for p_api in papers_api]
    for k in range(len(pdfs_titles)):
        overview_text += f'Paper {k+1}:"{pdfs_titles[k]}" - {papers_quickoverview[k]}\n'
    print('finished overview of the papers')
    return overview_text

def create_deep_dive(pdf_dir_path,deepdive_tamplate_path,papers_api):
    deepdive_text = ''
    with open(deepdive_tamplate_path, 'r') as file:
        deepdive_text += file.read() + '\n'
    pdfs_path = glob(f'{pdf_dir_path}/*.pdf')
    pdfs_titles = [extract_text_from_pdf(i).split('\n')[0] for i in pdfs_path]

    chat_text = "write a long description  of the paper, it should be separated to three parts: Abstract, Method and results.\n" \
                "Note that:\n\
                1. don't repeat on information you already said. \n \
                2. the results section should have examples of use cases for this new paper, and what it's innovated on."
    papers_explain = [ask_paper(p_api,chat_text) for p_api in papers_api]

    for k in range(len(pdfs_titles)):
        deepdive_text += f'Paper {k+1}: "{pdfs_titles[k]}"\
                        {papers_explain[k]}\n'

    return deepdive_text

def read_file(file_path):
    intreduction_tamplate_text = ''
    with open(file_path, 'r') as file:
        intreduction_tamplate_text += file.read() + '\n'
    return intreduction_tamplate_text

def create_speech(text,to_path):

    set_api_key(elevenlabs_api_key)
    print('generating speech')
    audio = generate(text=text)
    print('finish generating speech')
    save(audio, to_path)
    history = History.from_api()
    print(history)

def split_text_file(input_file_path, output_directory):
    # Read the content of the input file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into sentences (assuming sentences are separated by periods)
    sentences = content.split('.')

    # Create a list to hold the content of each new file
    new_files_content = []
    current_file_content = ""

    # Iterate through the sentences and form smaller files
    for sentence in sentences:
        sentence += '.'  # Add the period back to the end of the sentence
        if len(current_file_content) + len(sentence) <= 4500:
            current_file_content += sentence
        else:
            new_files_content.append(current_file_content)
            current_file_content = sentence

    # Add the last part if it's not empty
    if current_file_content:
        new_files_content.append(current_file_content)

    # Save the new files to the output directory
    base_filename = os.path.splitext(os.path.basename(input_file_path))[0]
    for i, content in enumerate(new_files_content):
        output_filename = f"{base_filename}_part{i + 1}.txt"
        output_file_path = os.path.join(output_directory, output_filename)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(content)


