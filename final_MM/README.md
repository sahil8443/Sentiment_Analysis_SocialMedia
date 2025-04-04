# Mind Matrix - Sentiment Analysis Tool

A Flask-based web application for sentiment analysis of CSV files using SVM and BERT models.

## Features

- User authentication (login/register)
- CSV file upload and analysis
- Sentiment analysis using SVM and BERT models
- Real-time results visualization
- Personalized recommendations
- Modern, responsive UI

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mindmatrix
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data:
```python
import nltk
nltk.download('stopwords')
```

## Project Structure

```
mindmatrix/
├── ap.py                 # Main Flask application
├── auth.py              # Authentication module
├── sentiment_analysis.py # Sentiment analysis module
├── requirements.txt     # Project dependencies
├── uploads/            # Directory for uploaded files
├── static/             # Static files (CSS, JS)
│   └── mind.css        # Custom styles
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Dashboard
│   ├── upload.html    # File upload page
│   ├── report.html    # Analysis report
│   ├── login.html     # Login page
│   ├── sign.html      # Registration page
│   └── home.html      # Landing page
└── models/            # Trained models
    ├── svm_sentiment_model.pkl
    └── tfidf_vectorizer.pkl
```

## Usage

1. Start the Flask application:
```bash
python ap.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Create an account or log in

4. Upload a CSV file with a 'text' column containing the content to analyze

5. View the analysis results and recommendations

## CSV File Format

Your CSV file should have at least one column named 'text' containing the content to analyze:

```csv
text
"This is a positive statement"
"This is a negative statement"
"This is a neutral statement"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 