# Resume Parser

## Description
The Resume Parser is a Python-based tool designed to extract and organize key information from resumes in PDF format. It uses regex and basic text processing techniques to identify and categorize essential data such as name, email, phone number, education, work experience, skills, certifications, awards, projects, and languages.

## Features
- Extracts text from PDF resumes.
- Identifies and categorizes key information using regex.
- Displays the extracted information in a readable format.

## Requirements
- Python 3.x
- pandas
- pdfplumber
- spacy
- logging

    ```
2. Change to the project directory:
    ```bash
    cd Resume-Parser
    ```
3. Create a virtual environment:
    ```bash
    python3 -m venv .venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
5. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the script:
    ```bash
    python main.py
    ```
2. Enter the exact path of your resume when prompted.

