# LinkStash

A FastAPI app for saving bookmarks and grouping them with tags.

## Install

From `LinkStash/`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
```

Set `JWT_SECRET_KEY`, `CSRF_SECRET_KEY`, and `DATABASE_URL` in `.env` (SQLite example: `sqlite:///./linkstash.db`).

```bash
alembic upgrade head
python seed.py
```

Seed users: `aayush@gmail.com` and `aayush2@gmail.com`, password `Test@123`.

## Run

```bash
python main.py
```

API at `http://localhost:8000`. Docs at `/docs`. Health at `GET /health`.

## Example curls

Get a token, then create a bookmark, list by tag, and attach a tag:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"aayush@gmail.com","password":"Test@123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/bookmarks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","title":"Example","notes":"demo"}'

curl -s "http://localhost:8000/bookmarks/?tag=python" \
  -H "Authorization: Bearer $TOKEN"

curl -s -X POST http://localhost:8000/bookmarks/1/tags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag_id":1}'
```
