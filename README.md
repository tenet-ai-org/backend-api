# TenetAI Backend API

FastAPI Backend for TenetAI.

## Setup + Local Testing

1. Install dependencies/requirements
```bash
pip install -r requirements.txt
```

2. Set up environment variables
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

3. Run localhost server

```bash
fastapi dev main.py
```

4. Then curl localhost

```bash
curl http://localhost:8000/
```