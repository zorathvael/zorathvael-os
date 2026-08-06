# Zorathvael OS — Developer Guide

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zorathvael/zorathvael-os.git
   cd zorathvael-os
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and provide your API keys
   ```

## Coding Standards
- Strictly adhere to **SOLID**, **DRY**, and **KISS** principles.
- Use explicit **type hints** for all function signatures.
- Write unit and integration tests for all new modules in the `test/` directory.
- Avoid all placeholders (`TODO`, `pass`, mock implementations) in production code.
