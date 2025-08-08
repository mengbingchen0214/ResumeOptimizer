import streamlit as st
from core import extract_text_from_file, get_deepseek_response

st.title("AI Resume Optimizer")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your DeepSeek API Key", type="password", help="Get your key from https://platform.deepseek.com/")

st.header("Resume Section")
resume_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=['pdf', 'docx'])

st.header("Job Description Section")
st.write("Choose one of the following two options:")

jd_text = st.text_area("Paste the Job Description Here", height=200)

st.write("OR")

jd_image = st.file_uploader("Upload Job Description as a screenshot (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

if st.button("Analyze"):
    if resume_file is None:
        st.error("Please upload your resume.")
    elif jd_text.strip() == "" and jd_image is None:
        st.error("Please provide a job description (either text or image).")
    else:
        with st.spinner("Analyzing... Please wait a moment."):
            try:
                resume_text = extract_text_from_file(resume_file)

                if jd_text.strip() != "":
                    job_description = jd_text
                else:
                    job_description = extract_text_from_file(jd_image)

                prompt = (f"你是一位专业的职业顾问。请以第一人称（“你”）的视角，根据以下简历和职位描述，进行直接、有重点的分析。分析内容应包括：\n"
                          f"1. 你的简历与职位描述的匹配度（用百分比数字表示）。\n"
                          f"2. 你的简历中哪些具体技能和经验是亮点，与职位要求高度吻合。\n"
                          f"3. 你的简历中有哪些地方存在明显不足或可以改进以更好地匹配职位要求。\n"
                          f"4. 针对这些不足，提出具体的、可操作的优化建议，例如如何重写某些句子或突出某些经历。\n"
                          f"请用专业的、直接的中文口吻，避免任何废话。直接从分析开始，无需寒暄。 "
                          f"简历内容：\n{resume_text}\n\n职位描述：\n{job_description}")

                response_text = get_deepseek_response(prompt, api_key=api_key if api_key else None)
                st.success("Analysis Complete!")
                st.markdown(response_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
