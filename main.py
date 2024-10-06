import os  # Works with the file system
import re  # Finds patterns in text
import spacy  # Handles language processing
import pdfplumber  # Reads PDFs
import logging  # Keeps track of program events

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('pdfminer').setLevel(logging.ERROR)

nlp = spacy.load('en_core_web_sm') #Loads the SpaCy language model

#Function for extracting the text from the resume
def extract_text(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
    return text

def extract_largest_text(file_path):
    largest_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text_data = page.extract_words()
                if not text_data:
                    continue
                # Find the text with the largest font size
                largest_texts = [text['text'] for text in text_data if float(text['height']) == max(float(word['height']) for word in text_data)]
                largest_text += " ".join(largest_texts) + " "
    except Exception as e:
        logging.error(f"Failed to extract largest text from PDF: {e}")
    return largest_text.strip()

def process_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_information(text):
    #dictionary for holding the data to be returned
    data = {}

    doc = nlp(text)
    email = None

    for i in doc.ents:
        if i.label_ == "EMAIL" and not email:
            email = i.text

    data['Email'] = email if email else 'N/A'

    # Find the phone number from the pdf
    phone_match = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    data['Phone'] = phone_match[0] if phone_match else 'N/A'

    #if the email is still None search it whithin the resume
    if not email:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        data['Email'] = email_match.group(0) if email_match else 'N/A'

    # Extract education details
    education_match = re.search(
        r'EDUCATION(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|TECHNICAL SKILLS|CERTIFICATIONS|PROJECTS|LANGUAGES|AWARDS|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Education'] = education_match.group(1).strip() if education_match else 'N/A'

    # Extract work experience
    experience_match = re.search(
        r'(?:EXPERIENCE|WORK EXPERIENCE)(.*?)(?=(TECHNICAL SKILLS|CERTIFICATIONS|PROJECTS|LANGUAGES|AWARDS|$))', text,
        re.DOTALL | re.IGNORECASE)
    data['Experience'] = experience_match.group(1).strip() if experience_match else 'N/A'

    # Extract skills
    skills_match = re.search(
        r'TECHNICAL SKILLS(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|EDUCATION|CERTIFICATIONS|PROJECTS|LANGUAGES|AWARDS|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Skills'] = skills_match.group(1).strip() if skills_match else 'N/A'

    # Extract certifications
    certification_match = re.search(
        r'(?:CERTIFICATION|CERTIFICATIONS)(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|EDUCATION|TECHNICAL SKILLS|PROJECTS|LANGUAGES|AWARDS|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Certifications'] = certification_match.group(1).strip() if certification_match else 'N/A'

    # Extract awards
    awards_match = re.search(
        r'(?:AWARD|AWARDS)(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|EDUCATION|TECHNICAL SKILLS|CERTIFICATIONS|PROJECTS|LANGUAGES|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Awards'] = awards_match.group(1).strip() if awards_match else 'N/A'

    # Extract projects
    projects_match = re.search(
        r'PROJECTS(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|EDUCATION|TECHNICAL SKILLS|CERTIFICATIONS|LANGUAGES|AWARDS|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Projects'] = projects_match.group(1).strip() if projects_match else 'N/A'

    languages_match = re.search(
        r'LANGUAGES(.*?)(?=(EXPERIENCE|WORK EXPERIENCE|EDUCATION|TECHNICAL SKILLS|CERTIFICATIONS|PROJECTS|AWARDS|$))',
        text, re.DOTALL | re.IGNORECASE)
    data['Languages'] = languages_match.group(1).strip() if languages_match else 'N/A'

    return data

def parse_resume(pdf_path):
    #initialize text with the text that was returned
    text = extract_text(pdf_path)
    text = process_text(text) #process the data
    data = extract_information(text) #Store the information in data

    # Extract the largest text
    largest_text = extract_largest_text(pdf_path)
    if largest_text:
        data['Name'] = largest_text

    return data

def display_resume(data):
    print("\nResume Information:\n")
    print("Name:".ljust(15), data['Name'])
    print("Email:".ljust(15), data['Email'])
    print("Phone:".ljust(15), data['Phone'])
    print("\nEducation:\n", data['Education'])
    print("\nExperience:\n", data['Experience'])
    print("\nSkills:\n", data['Skills'])
    print("\nCertifications:\n", data['Certifications'])
    print("\nAwards:\n", data['Awards'])
    print("\nProjects:\n", data['Projects'])
    print("\nLanguages:\n", data['Languages'])
    print("\n")

def main():
    pdf_path = input("Enter the exact path of your resume: ").strip()

    if not os.path.exists(pdf_path):
        logging.error("File not found")
        return

    try:
        parsed_data = parse_resume(pdf_path)

        if not parsed_data:
            logging.error("No data parsed from the resume")
            return

        display_resume(parsed_data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
