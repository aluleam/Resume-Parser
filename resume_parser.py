import spacy
from spacy.matcher import Matcher
from transformers import pipeline
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import pdfplumber
from collections import defaultdict
import logging
from pdf2image import convert_from_path
import pytesseract
from sentence_transformers import SentenceTransformer, util
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Step 2: Load NLP Models
def load_nlp_models():
    """Load spaCy and Hugging Face models."""
    try:
        nlp = spacy.load("en_core_web_sm")  # spaCy for basic NLP tasks
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn") 
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # Sentence Transformer for semantic similarity
        logging.info("NLP models loaded successfully.")
        return nlp, summarizer, sentence_model
    except Exception as e:
        logging.error(f"Error loading NLP models: {e}")
        raise

# Step 3: Extract Text from Resumes
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        if not text.strip():  # If no text is extracted, assume it's a scanned PDF
            logging.info("No text extracted from PDF. Attempting OCR.")
            text = extract_text_from_scanned_pdf(pdf_path)
        return text
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise

def extract_text_from_scanned_pdf(pdf_path):
    """Extract text from a scanned PDF using OCR."""
    try:
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.error(f"Error performing OCR on PDF: {e}")
        raise

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        raise

# Step 4: Parse Resume Information
def parse_resume(text, nlp):
    """Extract key information from resume text using spaCy."""
    try:
        doc = nlp(text)
        
        # Initialize a dictionary to store parsed data
        parsed_data = defaultdict(list)
        
        # Extract name (first entity recognized as a person)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                parsed_data["Name"] = ent.text
                break
        
        # Extract email
        email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        parsed_data["Email"] = email[0] if email else None
        
        # Extract phone number
        phone = re.findall(r"\(?\b\d{3}[-.)\s]?\d{3}[-.\s]?\d{4}\b", text)
        parsed_data["Phone"] = phone[0] if phone else None
        
        # Extract skills using spaCy's matcher
        matcher = Matcher(nlp.vocab)
        skills_list = ["Python", "Java", "Machine Learning", "SQL", "Data Analysis", "TensorFlow", "PyTorch", "NLP"]
        patterns = [[{"LOWER": skill.lower()}] for skill in skills_list]
        matcher.add("SKILLS", patterns)
        
        matches = matcher(doc)
        for match_id, start, end in matches:
            skill = doc[start:end].text
            if skill not in parsed_data["Skills"]:
                parsed_data["Skills"].append(skill)
        
        # Extract education (improved regex for degrees and institutions)
        education_patterns = [
            r"(?i)\b(?:B\.?A\.?|B\.?S\.?|Bachelor(?:'s)?)\b.*?\b(?:Computer Science|Engineering|Mathematics)\b",
            r"(?i)\b(?:M\.?S\.?|M\.?A\.?|Master(?:'s)?)\b.*?\b(?:Computer Science|Engineering|Mathematics)\b",
            r"(?i)\b(?:Ph\.?D\.?|Doctorate)\b.*?\b(?:Computer Science|Engineering|Mathematics)\b",
        ]
        for pattern in education_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                parsed_data["Education"].append(match.group().strip())
        
        # Extract experience (improved regex for job titles and companies)
        experience_patterns = [
            r"(?i)\b(?:Software Engineer|Data Scientist|Machine Learning Engineer)\b.*?\b(?:at|@)\b.*?\b(?:Google|Microsoft|Amazon)\b",
            r"(?i)\b(?:Intern|Internship)\b.*?\b(?:at|@)\b.*?\b(?:Google|Microsoft|Amazon)\b",
        ]
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                parsed_data["Experience"].append(match.group().strip())
        
        return parsed_data
    except Exception as e:
        logging.error(f"Error parsing resume: {e}")
        raise

# Step 5: Summarize Resume (Optional)
def summarize_resume(text, summarizer):
    """Summarize the resume text using Hugging Face Transformers."""
    try:
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        logging.error(f"Error summarizing resume: {e}")
        return "Summary not available."

# Step 6: Rank Applicants Based on Job Description
def rank_applicants(resumes, job_description, sentence_model):
    """Rank applicants based on semantic similarity between their skills and the job description."""
    try:
        # Compute embeddings for job description and resumes
        job_desc_embedding = sentence_model.encode(job_description, convert_to_tensor=True)
        resume_embeddings = sentence_model.encode([" ".join(resume["Skills"]) for resume in resumes], convert_to_tensor=True)
        
        # Compute cosine similarity between the job description and each resume
        cosine_similarities = util.pytorch_cos_sim(job_desc_embedding, resume_embeddings).flatten().tolist()
        
        # Rank resumes based on similarity scores
        ranked_indices = sorted(range(len(cosine_similarities)), key=lambda i: cosine_similarities[i], reverse=True)
        ranked_resumes = [(resumes[i], cosine_similarities[i]) for i in ranked_indices]
        
        return ranked_resumes
    except Exception as e:
        logging.error(f"Error ranking applicants: {e}")
        raise

# Step 7: Display Formatted Resume Information
def display_resume_info(resume, score=None):
    """Display parsed resume information in a structured format."""
    print("\n" + "=" * 50)
    if score:
        print(f"Rank (Score: {score:.2f})")
    print(f"Name: {resume.get('Name', 'N/A')}")
    print(f"Email: {resume.get('Email', 'N/A')}")
    print(f"Phone: {resume.get('Phone', 'N/A')}")
    print("\nSkills:")
    for skill in resume.get("Skills", []):
        print(f"  - {skill}")
    print("\nEducation:")
    for edu in resume.get("Education", []):
        print(f"  - {edu}")
    print("\nExperience:")
    for exp in resume.get("Experience", []):
        print(f"  - {exp}")
    print("\nSummary:")
    print(resume.get("Summary", "N/A"))
    print("=" * 50 + "\n")

# Step 8: Export Parsed Data to CSV
def export_to_csv(resumes, output_file="resumes.csv"):
    """Export parsed resume data to a CSV file."""
    try:
        data = []
        for resume in resumes:
            data.append({
                "Name": resume.get("Name", "N/A"),
                "Email": resume.get("Email", "N/A"),
                "Phone": resume.get("Phone", "N/A"),
                "Skills": ", ".join(resume.get("Skills", [])),
                "Education": ", ".join(resume.get("Education", [])),
                "Experience": ", ".join(resume.get("Experience", [])),
                "Summary": resume.get("Summary", "N/A")
            })
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        logging.info(f"Resume data exported to {output_file}.")
    except Exception as e:
        logging.error(f"Error exporting data to CSV: {e}")

# Step 9: Main Function
def main():
    try:
        # Load NLP models
        nlp, summarizer, sentence_model = load_nlp_models()
        
        # Ask the user to upload a resume
        resume_path = input("Enter the path to your resume (PDF or DOCX): ").strip()
        if not os.path.exists(resume_path):
            logging.error("File not found. Please check the path.")
            return
        
        if resume_path.endswith(".pdf"):
            text = extract_text_from_pdf(resume_path)
        elif resume_path.endswith(".docx"):
            text = extract_text_from_docx(resume_path)
        else:
            logging.error("Unsupported file format. Please upload a PDF or DOCX file.")
            return
        
        # Parse and summarize the resume
        parsed_data = parse_resume(text, nlp)
        summary = summarize_resume(text, summarizer)
        parsed_data["Summary"] = summary
        
        # Ask the user for the job description
        job_description = input("Enter the job description: ").strip()
        
        # Rank the applicant (in this case, just one resume)
        ranked_applicants = rank_applicants([parsed_data], job_description, sentence_model)
        
        # Display the parsed resume information
        for resume, score in ranked_applicants:
            display_resume_info(resume, score)
        
        # Export parsed data to CSV
        export_to_csv([parsed_data])
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()