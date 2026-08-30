# LinkStash frontend

Next.js app for the LinkStash API. Auth tokens live in `localStorage`. Axios retries failed requests after a queued refresh.

## Run

API first, from `LinkStash/`:

```bash
python main.py
```

Then this app:

```bash
cd LinkStashFrontend
bun install
cp .env.example .env.local
bun dev
```

Open [http://localhost:3000](http://localhost:3000). Seed login: `aayush@gmail.com` / `Test@123`.
