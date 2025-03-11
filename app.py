import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai
from fpdf import FPDF

# Configure Gemini
genai.configure(api_key="AIzaSyAkUOKHDBVJS0zx577VYHLPdMnUDj2E6Jk")
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text(file):
    """Extract text from PDF or DOCX files"""
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join(para.text for para in doc.paragraphs)
    return file.getvalue().decode("utf-8")

def analyze_resume(resume_text, job_desc_text):
    """Use Gemini to analyze skill gaps and suggest improvements with proper formatting"""
    prompt = f"""
    Analyze this resume against the job description and provide:
    1. Skill gaps
    2. Suggested improvements
    3. Optimized resume text in proper resume format
    
    The optimized resume must include these sections with proper formatting:
    - Name and Contact Information
    - Professional Summary
    - Skills (aligned with job requirements)
    - Work Experience (with relevant achievements)
    - Education
    - Certifications (if any)
    
    Maintain proper formatting with:
    - Clear section headings
    - Bullet points for achievements
    - Consistent spacing
    - Professional language
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_desc_text}
    """
    response = model.generate_content(prompt)
    return response.text

def create_pdf(content):
    """Create a PDF file from text with built-in Unicode support"""
    pdf = FPDF()
    pdf.add_page()
    # Use built-in font with Unicode support
    pdf.set_font('helvetica', '', 12)
    # Add content with proper encoding
    pdf.multi_cell(0, 10, txt=content.encode('latin1', 'replace').decode('latin1'))
    return pdf.output(dest='S').encode('latin1')

def create_docx(content):
    """Create a DOCX file from text"""
    doc = docx.Document()
    doc.add_paragraph(content)
    import io
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def main():
    st.title("AI Resume Optimizer")
    st.subheader("Upload your resume and job description for analysis")
    
    # File uploaders
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    job_desc_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    
    if resume_file and job_desc_file:
        with st.spinner("Analyzing..."):
            # Extract text
            resume_text = extract_text(resume_file)
            job_desc_text = extract_text(job_desc_file)
            
            # Analyze with Gemini
            analysis = analyze_resume(resume_text, job_desc_text)
            
            # Display results
            st.subheader("Analysis Results")
            st.write(analysis)
            
            # Download options
            st.subheader("Download Optimized Resume")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="Download as TXT",
                    data=analysis.encode('utf-8'),
                    file_name="optimized_resume.txt",
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    label="Download as PDF",
                    data=create_pdf(analysis),
                    file_name="optimized_resume.pdf",
                    mime="application/pdf"
                )
            with col3:
                st.download_button(
                    label="Download as DOCX",
                    data=create_docx(analysis),
                    file_name="optimized_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

if __name__ == "__main__":
    main() 