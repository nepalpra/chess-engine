# chess-engine

## How to run


1. Clone the repository: 
```bash
git clone https://github.com/nepalpra/chess-engine.git
cd chess-engine
```
2. Create a virtual environment:
    1. On macOS/Linux
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    2. On Windows
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Install Dependencies:
```bash
pip install -r requirements.txt
```

4. Run the project:
- `python3 main.py` runs the CLI version.
- `python3 main.py gui` runs the Pygame GUI version.