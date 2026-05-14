# DI Kiosk

A Flask-based AI kiosk app for HSLU Digital Ideation students to pick snacks via a sassy AI chatbot. The AI asks a few questions, roasts your life choices, and recommends a product from the inventory.

[Build log / wiki](wiki.md)

## Features

- AI chat with selectable personalities, powered by LiteLLM via Replicate
- Product browsing and checkout flow
- Tracks sold and declined counts per product
- Persistent chat session per kiosk use, with manual reset
- Auto-updating time/day context fed to the AI every minute

## Tech Stack

- **Backend:** Python, Flask
- **AI:** LiteLLM (Replicate)
- **Frontend:** Vanilla JS, Jinja2 templates

## Project Structure

```
kiosk-app-v2/
├── app.py               # Flask app, routes, AI logic
├── requirements.txt
├── .env                 # API keys (not tracked)
├── data/
│   ├── products.json    # Product inventory
│   ├── session.json     # Chat history
│   └── context.json     # Current time/day
├── static/
│   ├── script.js
│   ├── style.css
│   └── assets/
└── templates/
    ├── index.html
    ├── products.html
    ├── checkout.html
    └── ai.html
```

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
cd kiosk-app-v2
python -m venv venv
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create a `.env` file** in the root directory with your Replicate API key:

```
REPLICATE_API_KEY=your_key_here
```

**4. Populate `data/products.json`**

The `data/` folder is already in the repo. `session.json` and `context.json` are managed at runtime. You only need to replace the products in `products.json` with your own inventory.

Each product should follow this schema:

```json
[
  {
    "id": "unique-id",
    "name": "Product Name",
    "price": 2.50,
    "sold": 0,
    "declined": 0
  }
]
```

## Running

```bash
source venv/bin/activate
python app.py
```

The app runs at `http://localhost:5000` with debug mode on.