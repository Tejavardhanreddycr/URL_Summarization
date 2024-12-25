# Text Summarization Application

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.15.0+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/🦜️_LangChain-Latest-2F6FD2?style=for-the-badge)](https://www.langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=for-the-badge&labelColor=ef8336)](https://pycqa.github.io/isort/)

<div align="center">
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI" width="300"/>
  <br/>
  <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="Streamlit" width="300"/>
</div>

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

Text Summarization Application is a dual-interface tool that provides both API and web-based access to powerful text summarization capabilities. It leverages the Groq API and LangChain framework to generate concise summaries from YouTube videos and web pages.

The project consists of two main components:
1. A FastAPI-based REST API (`app.py`)
2. A Streamlit-based web interface (`streamlit_app.py`)

## Features

- 📝 Content Summarization
  - YouTube video transcripts
  - Web page content
  - Support for English language
  - Configurable summary length

- 🔧 Technical Features
  - RESTful API with FastAPI
  - Interactive web UI with Streamlit
  - Async processing
  - Rate limiting
  - Caching support

- 🔒 Security Features
  - API key authentication
  - Input validation
  - CORS support
  - SSL/TLS support

## Project Structure

```
text-summarization/
├── app.py                 # FastAPI application
├── streamlit_app.py       # Streamlit web interface
├── requirements.txt       # Project dependencies
├── tests/                 # Test files
├── docs/                  # Documentation
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Requirements

- Python 3.8+
- Groq API key ([Get one here](https://groq.com))
- Required packages:
  ```
  fastapi>=0.68.0
  streamlit>=1.15.0
  langchain
  langchain-groq
  python-dotenv
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/text-summarization.git
   cd text-summarization
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your credentials:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

## Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| GROQ_API_KEY | Groq API Key | Required |
| MAX_SUMMARY_LENGTH | Maximum summary length | 300 |
| ENABLE_CACHE | Enable response caching | True |
| LOG_LEVEL | Logging level | INFO |

## Usage

### FastAPI Application

1. Start the API server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

2. Access endpoints:
   - API documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Summarization endpoint: http://localhost:8000/summarize

### Streamlit Application

1. Start the web interface:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Open in browser:
   - http://localhost:8501

## API Documentation

### Endpoints

#### POST /summarize
Generates content summary.

Request:
```json
{
  "groq_api_key": "string",
  "url": "string"
}
```

Response:
```json
{
  "summary": "string"
}
```

For complete API documentation, visit `/docs` when the server is running.

## Development

### Code Style

This project uses:
- [Black](https://github.com/psf/black) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/) for linting

Format code before committing:
```bash
black .
isort .
flake8
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

Run tests using pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=.
```

## Deployment

### Docker Deployment

1. Build image:
   ```bash
   docker build -t text-summarization .
   ```

2. Run container:
   ```bash
   docker run -p 8000:8000 text-summarization
   ```

### Cloud Deployment

Deployment guides available for:
- AWS Elastic Beanstalk
- Google Cloud Run
- Heroku

See [deployment documentation](./docs/deployment.md) for details.

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Made with ❤️ using FastAPI, Streamlit, and LangChain</p>
  <p>© 2024 Your Name. All rights reserved.</p>
</div>
