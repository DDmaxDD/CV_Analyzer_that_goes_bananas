# CV Analyzer that goes bananas 🍌

A fun and interactive CV analyzer application built with Streamlit that helps analyze resumes for marketing automation roles. The app uses AI to provide detailed feedback on technical, marketing, and automation skills.

## Features

- Upload and analyze PDF and DOCX CVs
- AI-powered skill analysis
- Detailed feedback on technical, marketing, and automation skills
- Fun monkey-themed interface 🐒
- Comprehensive skill mapping and recommendations

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Dependencies

- streamlit
- PyPDF2
- python-docx
- pandas
- nltk
- scikit-learn
- openai
- python-dotenv

## License

MIT License 