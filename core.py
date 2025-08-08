import os
import io
import docx2txt
import PyPDF2
from PIL import Image
import pytesseract
from openai import OpenAI

# Set the path to the Tesseract executable. This is a common path on Mac with Homebrew.
# You may need to change this if your installation path is different.
try:
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
except Exception as e:
    print(f"Warning: Tesseract command not set. Image-to-text functionality may fail. Error: {e}")

# This is where your API key is read from the environment variable
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set.")

def extract_text_from_file(file):
    filename = file.name
    if filename.endswith('.docx'):
        text = docx2txt.process(file)
    elif filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    elif filename.endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(file)
        text = pytesseract.image_to_string(img)
    else:
        text = file.read().decode('utf-8')
    return text

def get_deepseek_response(prompt):
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",  # A powerful and free-tier model
        messages=[
            {"role": "system", "content": "你是一位专业的职业顾问。请以第一人称（“你”）的视角，根据简历和职位描述，进行直接、有重点、以中文书写的分析"},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content
