import os
import io
import docx2txt
import PyPDF2
from PIL import Image
import pytesseract
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI  # Use the standard OpenAI library for DeepSeek

# Set the path to the Tesseract executable. This is a common path on Mac with Homebrew.
# You may need to change this if your installation path is different.
try:
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
except Exception as e:
    print(f"Warning: Tesseract command not set. Image-to-text functionality may fail. Error: {e}")

app = Flask(__name__)
CORS(app)

# This is where your API key is read from the environment variable
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable not set.")
print(f"DeepSeek API key loaded: {DEEPSEEK_API_KEY[:4]}...{DEEPSEEK_API_KEY[-4:]}")


def extract_text_from_file(file):
    filename = file.filename
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = ""
    job_description = ""
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
    
    resume_file = request.files['resume']

    if 'job_description' in request.form:
        job_description = request.form['job_description']
    elif 'job_description' in request.files:
        job_description_file = request.files['job_description']
        job_description = extract_text_from_file(job_description_file)
    else:
        return jsonify({'error': 'No job description provided'}), 400

    try:
        resume_text = extract_text_from_file(resume_file)
        prompt = (f"你是一位专业的职业顾问。请以第一人称（“你”）的视角，根据以下简历和职位描述，进行直接、有重点的分析。分析内容应包括：\n"
                  f"1. 你的简历与职位描述的匹配度（用百分比数字表示）。\n"
                  f"2. 你的简历中哪些具体技能和经验是亮点，与职位要求高度吻合。\n"
                  f"3. 你的简历中有哪些地方存在明显不足或可以改进以更好地匹配职位要求。\n"
                  f"4. 针对这些不足，提出具体的、可操作的优化建议，例如如何重写某些句子或突出某些经历。\n"
                  f"请用专业的、直接的中文口吻，避免任何废话。直接从分析开始，无需寒暄。 "
                  f"简历内容：\n{resume_text}\n\n职位描述：\n{job_description}")
        
        response_text = get_deepseek_response(prompt)
        return jsonify({'analysis': response_text})
    except Exception as e:
        # This will catch and print any specific error, which is helpful for debugging
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)