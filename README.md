# Resume-Parser

## Overview
The Resume Parser is a Python application designed to extract and process key information from resume PDF files. It uses Natural Language Processing (NLP) with spaCy and PDF processing with pdfplumber to accurately extract details such as name, email, phone number, education, work experience, and technical skills. The extracted information is displayed in a user-friendly format and saved to an Excel file for further use.

## Features
- Extracts and processes text from PDF resumes
- Identifies and extracts key information:
  - Name
  - Email
  - Phone number
  - Education
  - Work experience
  - Technical skills
- Displays extracted information in a readable format
- Saves extracted information to an Excel file

## Requirements
- Python 3.x
- pandas
- pdfplumber
- spacy
- pdfminer.six
- openpyxl

## Installation
1. **Clone the repository:**
    ```bash
    git clone https://github.com/aluleam/resume-parser.git
    cd resume-parser
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

## Usage
1. **Run the script:**
    ```bash
    python main.py
    ```

2. **Follow the prompt to enter the path of your resume PDF:**
    ```plaintext
    Enter the exact path of your resume: /path/to/your/resume.pdf
