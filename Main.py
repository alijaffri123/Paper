import streamlit as st
import requests
from fpdf import FPDF
import tempfile
import os

# Configuration
OLLAMA_MODEL = "phi3"  # change to model you have pulled, like "llama3", "gemma", etc.
OLLAMA_URL = "http://localhost:11434/api/generate"

# Function to query Ollama
def generate_paper(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json().get("response", "❌ No response text found.")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Ollama Error: {e}")
        return ""

# Function to create PDF
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)

    # Save to a temporary file
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_path.name)
    return temp_path.name

# Streamlit UI
st.set_page_config(page_title="📝 AI Question Paper Generator", layout="centered")
st.title("📄 Question Paper Generator (Ollama)")

with st.form("paper_form", clear_on_submit=False):
    grade = st.selectbox("Select Grade", ["Grade 8", "Grade 9", "Grade 10"])
    subject = st.selectbox("Select Subject", ["Mathematics", "Physics", "Chemistry", "Biology"])
    topic = st.text_input("Enter Topic (e.g., Algebra, Force, Stoichiometry)")
    difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
    num_mcqs = st.slider("Number of MCQs", 1, 10, 3)
    num_short = st.slider("Number of Short Questions", 1, 5, 2)
    num_long = st.slider("Number of Long Questions", 1, 3, 1)
    submitted = st.form_submit_button("Generate Paper")

if submitted:
    with st.spinner("⏳ Generating with Ollama..."):
        prompt = f"""
You are a question paper generator.

Generate a {grade} level question paper for {subject}, topic: "{topic}", difficulty: {difficulty}.

Include:
- Section A: {num_mcqs} MCQs (each with 4 options, and mark the correct answer)
- Section B: {num_short} Short Questions (5 marks each)
- Section C: {num_long} Long Questions (10 marks each)

Use exam format and avoid question repetition.
"""
        paper = generate_paper(prompt)
        if paper:
            st.success("✅ Question paper generated!")
            st.text_area("Preview", paper, height=400)

            # PDF Download
            pdf_path = create_pdf(paper)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download as PDF", f, file_name="question_paper.pdf")

            os.remove(pdf_path)
