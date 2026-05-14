# DI Kiosk — Build Log

A chronological account of how the app was built.

---

## Week 1 — Experimenting with LiteLLM (Apr 28)

The project started with a basic Flask app and early experiments connecting to an LLM via LiteLLM. The first real commit added `context.json` and `history.json` to test how context could be fed into the AI. No frontend yet — just testing the AI connection from the backend.

---

## Week 2 — Core AI Loop (May 1–4)

**May 1** — First working AI interaction. A minimal frontend was built (`index.html`, `script.js`) and the backend was wired up to send messages and receive responses. `session.json` was introduced to track the conversation.

**May 3** — The prompt structure was reworked into what became the "mega prompt": a single system message combining instructions, session history, context, and available products. Session saving to JSON was added, meaning conversation history now persisted across messages within a session. A background thread was added to auto-update `context.json` every 60 seconds with the current time and day — giving the AI live awareness of when it's running. The session was set to reset automatically on page reload.

A personality dropdown was also integrated, letting the user pick the AI's personality before starting a chat, which gets passed as part of the prompt.

**May 4** — The AI's output format was locked down. The response schema (`message`, `options`, `product_name`, `product_id`) was defined and the frontend was updated to parse and render it properly. The app was switched from a generic LiteLLM setup to routing through **Replicate** specifically. A "steps" system was briefly explored — the idea of only sending the AI what it needs at each step of the conversation — but this was later rolled back in favour of the full context approach.

---

## Week 3 — Full Kiosk App (May 10–11)

**May 10** — The app expanded from a single chat page into a full multi-page kiosk. Four routes were implemented:

- `/` — home/landing page
- `/products.html` — product grid loaded from `products.json`
- `/checkout.html` — checkout view for a selected product, with TWINT QR code
- `/ai.html` — the AI chat interface

Product images and per-product TWINT QR codes were added to `static/assets/`. The checkout button was wired into the AI flow so that after the AI recommends a product, clicking it navigates directly to that product's checkout page.

**May 11** — The mega prompt was polished significantly. `sold` and `declined` counters were added to each product in `products.json`, with two new backend routes (`/increment_sold`, `/increment_declined`) to update them on user interaction. This gave the AI access to real sales data, which it uses to roast the group's collective habits. `history.json` was removed — it had been unused.

Multiple models were tested via Replicate to find the best balance of speed, quality, and interaction style. Notes on each are left as comments in `app.py`.

---

## Repo Cleanup (May 12–14)

Data files were untacked from git using `git update-index --skip-worktree` so that runtime changes don't show up as uncommitted changes. The `data/` folder itself remains in the repo so cloners don't have to create it manually.