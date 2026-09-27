# Contributing to Corporate Brain

## Local Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`

## Running Tests
We enforce strict testing and linting. Before opening a Pull Request, run:
- Linting: `ruff check .`
- Testing: `pytest test_supervisor.py`

## Git Workflow
Please do not push directly to `main`. Create a feature branch (`git checkout -b feature/your-feature`) and open a Pull Request.