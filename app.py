from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import socket

START_TIME = time.time()

HTML_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes Monitoring App</title>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', sans-serif;

            background: linear-gradient(
                135deg,
                #0f172a,
                #1e293b,
                #0f766e
            );

            overflow: hidden;
        }}

        .card {{
            width: 700px;
            padding: 40px;
            border-radius: 24px;

            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(15px);

            border: 1px solid rgba(255, 255, 255, 0.15);

            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);

            text-align: center;
            color: white;
        }}

        .badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 50px;

            background: #0284c7;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
        }}

        h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            color: #ffffff;
        }}

        .version {{
            color: #cbd5e1;
            font-size: 18px;
            margin-bottom: 25px;
        }}

        .status {{
            display: inline-flex;
            align-items: center;
            gap: 10px;

            background: #16a34a;
            padding: 14px 24px;
            border-radius: 12px;

            font-weight: bold;
            font-size: 18px;

            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{
                box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.6);
            }}
            70% {{
                box-shadow: 0 0 0 20px rgba(22, 163, 74, 0);
            }}
            100% {{
                box-shadow: 0 0 0 0 rgba(22, 163, 74, 0);
            }}
        }}

        .metrics {{
            margin-top: 30px;

            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .metric {{
            background: rgba(255, 255, 255, 0.05);
            padding: 18px;
            border-radius: 12px;
            transition: transform 0.25s ease, background 0.25s ease;
        }}

        .metric:hover {{
            transform: translateY(-6px);
            background: rgba(255,255,255,0.12);
        }}

        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #38bdf8;
            word-break: break-word;
        }}

        .metric-label {{
            margin-top: 5px;
            color: #cbd5e1;
            font-size: 14px;
        }}

        .footer {{
            margin-top: 30px;
            color: #94a3b8;
            font-size: 14px;
        }}
    </style>
</head>

<body>

<div class="card">

    <div class="badge">
        ☸ Kubernetes Dashboard
    </div>

    <h1>🚀 Kubernetes Monitoring App</h1>

    <div class="version">
        Version 5 Successfully Deployed
    </div>

    <div class="status">
        ✅ Application Running Healthy
    </div>

    <div class="metrics">

        <div class="metric">
            <div class="metric-value">3</div>
            <div class="metric-label">Pods</div>
        </div>

        <div class="metric">
            <div class="metric-value">100%</div>
            <div class="metric-label">Availability</div>
        </div>

        <div class="metric">
            <div class="metric-value">0</div>
            <div class="metric-label">Errors</div>
        </div>

        <div class="metric">
            <div class="metric-value">{socket.gethostname()}</div>
            <div class="metric-label">Pod Hostname</div>
        </div>

    </div>

    <div class="footer">
        Cluster Status: Operational • Ready for HPA Testing
        <br><br>
        Server Time: <span id="time"></span>
    </div>

</div>

<script>
function updateTime() {{
    document.getElementById("time").textContent =
        new Date().toLocaleTimeString();
}}

updateTime();
setInterval(updateTime, 1000);
</script>

</body>
</html>
"""


class AppHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Simulate slight processing delay (helps HPA testing)
        time.sleep(0.2)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(HTML_PAGE.encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), AppHandler)

    print("🚀 Server running on port 8000...")
    print(f"📦 Pod Hostname: {socket.gethostname()}")

    server.serve_forever()