# Running the Qwen3 API Service

Follow these steps to set up the environment and run the API service.

## 1. Set up Virtual Environment

If you haven't already, create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
# .venv\Scripts\activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Download the Model

```bash
# Download 8B model (default)
python src/downloader.py --model 8b

# Download 4B model
python src/downloader.py --model 4b

# Force re-download if a file is corrupted
python src/downloader.py --model 4b --force
```

## 4. Run the API Service

```bash
python src/main.py
```

The service will be available at `http://localhost:9000`.

## 5. Testing

You can access the built-in testing UI by opening `http://localhost:9000` in your web browser.
