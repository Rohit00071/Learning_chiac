import os
import sys
from pathlib import Path

root = Path(__file__).parent.parent
os.chdir(str(root))
sys.path.insert(0, str(root))

os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8000")
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

async def app(scope, receive, send):
    assert scope["type"] in ("http", "websocket")

    if scope["type"] == "websocket":
        await handle_websocket(scope, receive, send)
        return

    path = scope["path"]

    if path.startswith("/_stcore") or path.startswith("/stream"):
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"text/plain"]],
        })
        await send({"type": "http.response.body", "body": b"Streamlit server not available in serverless mode"})
        return

    html = INDEX_HTML
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [[b"content-type", b"text/html; charset=utf-8"]],
    })
    await send({"type": "http.response.body", "body": html.encode()})

async def handle_websocket(scope, receive, send):
    await send({"type": "websocket.close", "code": 1000})

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Learning Analytics Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; }
    .card { background: white; padding: 3rem; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 640px; width: 100%; text-align: center; }
    .icon { font-size: 4rem; margin-bottom: 1rem; }
    h1 { color: #1f77b4; font-size: 1.8rem; margin-bottom: 0.5rem; }
    p { color: #555; line-height: 1.6; margin-bottom: 1rem; }
    .badge { display: inline-block; background: #e8f0fe; color: #1f77b4; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 1.5rem; }
    .btn { display: inline-block; background: #1f77b4; color: white; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; transition: background 0.2s; margin: 0.5rem; }
    .btn:hover { background: #155a8a; }
    .btn-secondary { background: #28a745; }
    .btn-secondary:hover { background: #1e7e34; }
    .code { background: #f5f5f5; padding: 12px 16px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; margin: 1rem 0; display: inline-block; }
    .features { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 1.5rem 0; text-align: left; }
    .feature { padding: 0.75rem; background: #f8f9fa; border-radius: 8px; border-left: 3px solid #1f77b4; font-size: 0.9rem; color: #333; }
    hr { border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }
    .footer { color: #999; font-size: 0.8rem; margin-top: 1.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">🎓</div>
    <h1>AI Learning Analytics Dashboard</h1>
    <div class="badge">Deployed on Vercel</div>
    <p>Multi-agent AI platform for analyzing learner data with actionable insights, clustering, risk prediction, and personalized recommendations.</p>
    <div class="features">
      <div class="feature">📊 Performance Analytics</div>
      <div class="feature">🧠 ML Clustering</div>
      <div class="feature">⚠️ Risk Prediction</div>
      <div class="feature">💡 Smart Insights</div>
      <div class="feature">🎯 Recommendations</div>
      <div class="feature">✅ Validation Reports</div>
    </div>
    <hr>
    <p style="font-size:0.9rem;"><strong>Run the full interactive dashboard:</strong></p>
    <div class="code">streamlit run dashboard/app.py</div>
    <br>
    <a class="btn btn-secondary" href="https://streamlit.io/cloud" target="_blank">Deploy on Streamlit Cloud</a>
    <div class="footer">Built with Python, Streamlit &amp; scikit-learn</div>
  </div>
</body>
</html>"""
