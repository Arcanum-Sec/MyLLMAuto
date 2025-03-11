# MyLLMAuto CTF

This is a ( WIP :construction: ) Capture The Flag (CTF) application designed to teach prompt injection in multi-chain LLM applications. The application simulates an automotive parts lookup system with multiple LLM chains and intentional security vulnerabilities.

## Challenge Overview

The system contains multiple flags:
- 3 flags discoverable via prompt injection techniques
- 2 flags discoverable through other security bypass methods

All flags follow the format `realflag={flag_text}` or `realflag=flag_text`.

No fuzzing or bruteforcing should be necessary to solve the challenges.

## Setup

### Option 1: Local Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The application will be available at http://localhost:8001.

**Note:** You'll need to provide your OpenAI API key in the application UI.

### Option 2: Docker Installation

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Build and run the Docker container:
```bash
docker-compose up -d
```

4. To stop the application:
```bash
docker-compose down
```

The application will be available at http://localhost:8001.

**Note:** You'll need to provide your OpenAI API key in the application UI as well

## Application Structure

- `main.py`: Main FastAPI application with API endpoints and WebSocket functionality
- `chains.py`: LLM chain definitions with intentional vulnerabilities
- `parts_db.py`: Mock parts database with sensitive information
- `employee_db.py`: Employee database with sensitive information
- `engineering_notes.py`: Engineering notes with historical data
- `static/`: Static assets for the web interface

## Features

### Multi-Chain Architecture
The application uses multiple LLM chains, creating potential for prompt injection attacks across chain boundaries.

### Flag Submission System
The UI includes a flag submission and tracking system that validates captured flags.

## LLM Integration

This application uses:
- OpenAI GPT-3.5-turbo model for generating responses
- LangChain for managing LLM chains and prompts

## Disclaimer

This application is designed for educational purposes only. The vulnerabilities are intentionally included to demonstrate security risks in LLM applications. Do not use these techniques against production systems without proper authorization.

## Credits

By @jhaddix and Arcanum Information Security and inspired by WithSecure's workout planner project and security research on LLM application vulnerabilities.
