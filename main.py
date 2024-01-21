
import os
from openai import OpenAI
import streamlit as st
import ast
from PyPDF2 import PdfReader
from docx import Document

def extract_content(uploaded_file):
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == '.pdf':
            return extract_pdf_content(uploaded_file)
        elif file_extension == '.docx':
            return extract_docx_content(uploaded_file)
        else:
            print(f'Unsupported file format: {file_extension}')
            return None
    except Exception as error:
        print(f'Got error in "extract_content": {error}')
        return None

def extract_pdf_content(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)
        content = ''
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            content += page.extract_text()
        return content
    except Exception as error:
        print(f'Got error in "extract_pdf_content" : {error}')
        return None
def extract_docx_content(uploaded_file):
    try:
        doc = Document(uploaded_file)
        content = ''
        for paragraph in doc.paragraphs:
            content += paragraph.text + '\n'
        return content
    except Exception as error:
        print(f'Got error in "extract_docx_content": {error}')
        return None

def handling_gpt_ouput(gpt_response):
    try:
        parsed_variable = ast.literal_eval(gpt_response)
        if isinstance(parsed_variable, list):
            return parsed_variable
    except (ValueError, SyntaxError):
        pass
    start_index = gpt_response.find('{')
    end_index = gpt_response.rfind('}')
    try:
        if start_index != -1 and end_index != -1:
            extracted_content = gpt_response[start_index:end_index + 1]
            output = eval(extracted_content)
            return  [output]
    except:
        pass
    return []

def extract_information_from_text(extracted_statement):
    client = OpenAI()
    client.api_key = os.getenv('OPENAI_API_KEY')
    #model_engine = "gpt-3.5-turbo-1106"
    model_engine = "gpt-4-1106-preview"
    system = '''
    You are HR manager of a company whose task is to analyze the resume provided by candidate and extract the Job designation in which the candidate skills fits. \n
    And be specific to resume content as per their summary and the whole data provided. And tell how much
    CTC salary you would offer in INR based on the overall summary,\n
    And remember that our budget is low.
    '''
    prompt2=f''' Give me the Job role, designation name,latest degree or college or course, salary, work experience in year and list only their top skills in which candidate worked more. \n
    do not explain everything for below resume content: {extracted_statement}'''
    prompt3=f''' Return everything in JSON format.'''
    conversation1 = [{'role': 'system', 'content': system},{'role': 'user', 'content': prompt2},{'role': 'user', 'content': prompt3}]
    response = client.chat.completions.create(model=model_engine,messages=conversation1,temperature = 0)
    jsonify_response = response.choices[0].message.content
    #output = handling_gpt_ouput(jsonify_response)
    return jsonify_response

def app_layout(uploaded_file):
    extracted_data = extract_content(uploaded_file)
    print(extracted_data)

    if extracted_data is not None:
        response_text = extract_information_from_text(extracted_data)
        output=response_text
        st.write(output)
        return  response_text
    else:
        st.write('PDF Extraction Failed!')
        return  None

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    with open("style.css") as source_des:
        st.markdown(f"<style>{source_des.read()}</style>", unsafe_allow_html=True)
    st.title("Resume Reviewer")
    uploaded_file = st.file_uploader("Upload Resume 👇🏻")
    if uploaded_file is None:
        st.write("Waiting for file upload...")
    if uploaded_file is not None:
        button = st.button("Generate Summary 📝")
        if button:
            with st.spinner("Processing..."):
                app_layout(uploaded_file)