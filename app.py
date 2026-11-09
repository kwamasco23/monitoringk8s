
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time
import socket
import os

import psutil
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


START_TIME = time.time()
REQUEST_COUNT = Counter(
    "monitoring_app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "monitoring_app_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
)

CPU_USAGE = Gauge(
    "monitoring_app_cpu_usage_percent",
    "Application host CPU usage percentage",
)

MEMORY_USAGE = Gauge(
    "monitoring_app_memory_usage_percent",
    "Application host memory usage percentage",
)


APP_VERSION = os.getenv("APP_VERSION", "v5")


def get_uptime():
    seconds = int(time.time() - START_TIME)

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days:
        return f"{days}d {hours}h {minutes}m {seconds}s"

    if hours:
        return f"{hours}h {minutes}m {seconds}s"

    if minutes:
        return f"{minutes}m {seconds}s"

    return f"{seconds}s"


def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)


def get_status_data():
    update_system_metrics()

    memory = psutil.virtual_memory()

    return {
        "status": "Healthy",
        "version": APP_VERSION,
        "hostname": socket.gethostname(),
        "uptime": get_uptime(),
        "requests": REQUEST_COUNTER_VALUE[0],
        "cpu": round(psutil.cpu_percent(interval=None), 1),
        "memory": round(memory.percent, 1),
        "memory_available": round(memory.available / 1024 / 1024, 1),
        "python": "3.11",
        "port": 8000,
        "environment": "Kubernetes",
    }


REQUEST_COUNTER_VALUE = [0]


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Kubernetes Operations Dashboard</title>

    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-main: #07111f;
            --bg-secondary: #0d1b2e;
            --card: rgba(255, 255, 255, 0.06);
            --card-border: rgba(255, 255, 255, 0.10);
            --text: #f8fafc;
            --muted: #94a3b8;
            --blue: #38bdf8;
            --green: #22c55e;
            --cyan: #06b6d4;
        }

        body {

            min-height: 100vh;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            color: var(--text);

            background:

                radial-gradient(
                    circle at 10% 10%,
                    rgba(14, 165, 233, 0.18),
                    transparent 30%
                ),

                radial-gradient(
                    circle at 90% 90%,
                    rgba(20, 184, 166, 0.16),
                    transparent 30%
                ),

                linear-gradient(
                    135deg,
                    var(--bg-main),
                    var(--bg-secondary)
                );

            padding: 40px 20px;

        }


        .container {

            width: 100%;
            max-width: 1100px;
            margin: auto;

        }


        .topbar {

            display: flex;
            justify-content: space-between;
            align-items: center;

            margin-bottom: 30px;

            gap: 20px;

        }


        .brand {

            display: flex;
            align-items: center;
            gap: 15px;

        }


        .brand-icon {

            width: 52px;
            height: 52px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 15px;

            background:
                linear-gradient(
                    135deg,
                    #0284c7,
                    #06b6d4
                );

            font-size: 25px;

            box-shadow:
                0 10px 30px
                rgba(6, 182, 212, 0.25);

        }


        .brand h1 {

            font-size: 22px;
            font-weight: 700;

        }


        .brand p {

            margin-top: 4px;

            color: var(--muted);

            font-size: 13px;

        }


        .environment {

            padding: 10px 16px;

            border-radius: 50px;

            background: rgba(34, 197, 94, 0.10);

            border:
                1px solid
                rgba(34, 197, 94, 0.25);

            color: #86efac;

            font-size: 13px;
            font-weight: 600;

        }


        .hero {

            position: relative;

            overflow: hidden;

            padding: 35px;

            border-radius: 24px;

            background:
                linear-gradient(
                    135deg,
                    rgba(14, 165, 233, 0.12),
                    rgba(20, 184, 166, 0.08)
                );

            border:
                1px solid
                var(--card-border);

            backdrop-filter: blur(20px);

            box-shadow:
                0 25px 60px
                rgba(0, 0, 0, 0.25);

            margin-bottom: 20px;

        }


        .hero::after {

            content: "";

            position: absolute;

            width: 250px;
            height: 250px;

            border-radius: 50%;

            background:
                rgba(56, 189, 248, 0.08);

            right: -100px;
            top: -100px;

        }


        .hero-label {

            color: var(--blue);

            font-size: 13px;

            font-weight: 700;

            letter-spacing: 1.5px;

            text-transform: uppercase;

            margin-bottom: 12px;

        }


        .hero h2 {

            font-size: clamp(28px, 5vw, 44px);

            line-height: 1.1;

            margin-bottom: 12px;

        }


        .hero-description {

            color: var(--muted);

            max-width: 650px;

            line-height: 1.6;

            font-size: 15px;

        }


        .status-row {

            display: flex;

            align-items: center;

            gap: 12px;

            margin-top: 25px;

        }


        .status {

            display: inline-flex;

            align-items: center;

            gap: 10px;

            padding: 12px 18px;

            border-radius: 12px;

            background:
                rgba(34, 197, 94, 0.12);

            border:
                1px solid
                rgba(34, 197, 94, 0.25);

            color: #86efac;

            font-weight: 700;

            font-size: 14px;

        }


        .status-dot {

            width: 9px;
            height: 9px;

            border-radius: 50%;

            background: var(--green);

            box-shadow:
                0 0 0 5px
                rgba(34, 197, 94, 0.12);

            animation: pulse 2s infinite;

        }


        @keyframes pulse {

            0% {
                box-shadow:
                    0 0 0 0
                    rgba(34, 197, 94, 0.5);
            }

            70% {
                box-shadow:
                    0 0 0 10px
                    rgba(34, 197, 94, 0);
            }

            100% {
                box-shadow:
                    0 0 0 0
                    rgba(34, 197, 94, 0);
            }

        }


        .grid {

            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 16px;

            margin-bottom: 20px;

        }


        .card {

            padding: 22px;

            border-radius: 18px;

            background: var(--card);

            border:
                1px solid
                var(--card-border);

            backdrop-filter: blur(15px);

            transition:
                transform 0.2s ease,
                background 0.2s ease;

        }


        .card:hover {

            transform: translateY(-4px);

            background:
                rgba(255, 255, 255, 0.09);

        }


        .card-header {

            display: flex;

            justify-content: space-between;

            align-items: center;

            margin-bottom: 18px;

        }


        .card-title {

            color: var(--muted);

            font-size: 13px;

            font-weight: 600;

        }


        .card-icon {

            font-size: 18px;

            opacity: 0.8;

        }


        .metric {

            font-size: 25px;

            font-weight: 700;

            color: var(--blue);

            word-break: break-word;

        }


        .metric-small {

            font-size: 13px;

            color: var(--muted);

            margin-top: 7px;

        }


        .wide-grid {

            display: grid;

            grid-template-columns:
                1fr 1fr;

            gap: 20px;

            margin-bottom: 20px;

        }


        .panel {

            padding: 25px;

            border-radius: 20px;

            background: var(--card);

            border:
                1px solid
                var(--card-border);

            backdrop-filter: blur(15px);

        }


        .panel h3 {

            font-size: 16px;

            margin-bottom: 20px;

        }


        .info-row {

            display: flex;

            justify-content: space-between;

            align-items: center;

            gap: 20px;

            padding: 13px 0;

            border-bottom:
                1px solid
                rgba(255,255,255,0.06);

        }


        .info-row:last-child {

            border-bottom: none;

        }


        .info-label {

            color: var(--muted);

            font-size: 13px;

        }


        .info-value {

            color: var(--text);

            font-size: 13px;

            font-weight: 600;

            text-align: right;

            word-break: break-word;

        }


        .progress-container {

            margin-top: 15px;

        }


        .progress-header {

            display: flex;

            justify-content: space-between;

            margin-bottom: 8px;

            font-size: 12px;

            color: var(--muted);

        }


        .progress {

            height: 8px;

            background:
                rgba(255,255,255,0.08);

            border-radius: 50px;

            overflow: hidden;

        }


        .progress-bar {

            height: 100%;

            width: 0%;

            border-radius: 50px;

            background:
                linear-gradient(
                    90deg,
                    #0284c7,
                    #06b6d4
                );

            transition:
                width 0.5s ease;

        }


        .footer {

            text-align: center;

            color: var(--muted);

            font-size: 12px;

            padding: 20px;

        }


        @media (max-width: 850px) {

            .grid {

                grid-template-columns:
                    repeat(2, 1fr);

            }

            .wide-grid {

                grid-template-columns: 1fr;

            }

        }


        @media (max-width: 550px) {

            body {

                padding: 20px 12px;

            }

            .topbar {

                align-items: flex-start;

                flex-direction: column;

            }

            .hero {

                padding: 25px;

            }

            .grid {

                grid-template-columns: 1fr;

            }

        }

    </style>

</head>


<body>

<div class="container">


    <div class="topbar">

        <div class="brand">

            <div class="brand-icon">
                ☸
            </div>

            <div>

                <h1>Kubernetes Operations</h1>

                <p>
                    Application Runtime Dashboard
                </p>

            </div>

        </div>


        <div class="environment">

            ● Kubernetes Cluster

        </div>

    </div>


    <section class="hero">

        <div class="hero-label">
            Production-style Lab Environment
        </div>

        <h2>
            Monitoring Application
        </h2>

        <p class="hero-description">

            A lightweight Kubernetes workload exposing
            application health, runtime information and
            Prometheus metrics for observability and
            autoscaling experiments.

        </p>


        <div class="status-row">

            <div class="status">

                <span class="status-dot"></span>

                APPLICATION HEALTHY

            </div>

        </div>

    </section>


    <div class="grid">


        <div class="card">

            <div class="card-header">

                <span class="card-title">
                    APPLICATION
                </span>

                <span class="card-icon">
                    🚀
                </span>

            </div>

            <div
                class="metric"
                id="version"
            >
                Loading...
            </div>

            <div class="metric-small">
                Current release
            </div>

        </div>


        <div class="card">

            <div class="card-header">

                <span class="card-title">
                    POD
                </span>

                <span class="card-icon">
                    ☸
                </span>

            </div>

            <div
                class="metric"
                id="hostname"
            >
                Loading...
            </div>

            <div class="metric-small">
                Container hostname
            </div>

        </div>


        <div class="card">

            <div class="card-header">

                <span class="card-title">
                    UPTIME
                </span>

                <span class="card-icon">
                    ⏱
                </span>

            </div>

            <div
                class="metric"
                id="uptime"
            >
                Loading...
            </div>

            <div class="metric-small">
                Since container start
            </div>

        </div>


        <div class="card">

            <div class="card-header">

                <span class="card-title">
                    REQUESTS
                </span>

                <span class="card-icon">
                    📡
                </span>

            </div>

            <div
                class="metric"
                id="requests"
            >
                0
            </div>

            <div class="metric-small">
                Requests processed
            </div>

        </div>


    </div>


    <div class="wide-grid">


        <div class="panel">

            <h3>
                Runtime Information
            </h3>


            <div class="info-row">

                <span class="info-label">
                    Hostname
                </span>

                <span
                    class="info-value"
                    id="hostname2"
                >
                    -
                </span>

            </div>


            <div class="info-row">

                <span class="info-label">
                    Runtime
                </span>

                <span class="info-value">
                    Python 3.11
                </span>

            </div>


            <div class="info-row">

                <span class="info-label">
                    Port
                </span>

                <span class="info-value">
                    8000/TCP
                </span>

            </div>


            <div class="info-row">

                <span class="info-label">
                    Environment
                </span>

                <span class="info-value">
                    Kubernetes
                </span>

            </div>


            <div class="info-row">

                <span class="info-label">
                    Metrics
                </span>

                <span class="info-value">
                    /metrics
                </span>

            </div>


        </div>


        <div class="panel">

            <h3>
                Resource Utilisation
            </h3>


            <div class="progress-container">

                <div class="progress-header">

                    <span>
                        CPU Usage
                    </span>

                    <span id="cpu-label">
                        0%
                    </span>

                </div>

                <div class="progress">

                    <div
                        class="progress-bar"
                        id="cpu-bar"
                    ></div>

                </div>

            </div>


            <div class="progress-container">

                <div class="progress-header">

                    <span>
                        Memory Usage
                    </span>

                    <span id="memory-label">
                        0%
                    </span>

                </div>

                <div class="progress">

                    <div
                        class="progress-bar"
                        id="memory-bar"
                    ></div>

                </div>

            </div>


            <div
                class="info-row"
                style="margin-top: 20px;"
            >

                <span class="info-label">
                    Memory Available
                </span>

                <span
                    class="info-value"
                    id="memory-available"
                >
                    -
                </span>

            </div>


        </div>


    </div>


    <div class="footer">

        Kubernetes Monitoring App
        •
        Prometheus Ready
        •
        HPA Ready

        <br><br>

        Last updated:
        <span id="last-update">
            -
        </span>

    </div>


</div>


<script>

async function updateDashboard() {

    try {

        const response =
            await fetch("/api/status", {
                cache: "no-store"
            });

        const data =
            await response.json();


        document.getElementById("version")
            .textContent = data.version;

        document.getElementById("hostname")
            .textContent = data.hostname;

        document.getElementById("hostname2")
            .textContent = data.hostname;

        document.getElementById("uptime")
            .textContent = data.uptime;

        document.getElementById("requests")
            .textContent =
            data.requests.toLocaleString();


        const cpu =
            Math.min(data.cpu, 100);

        const memory =
            Math.min(data.memory, 100);


        document.getElementById("cpu-label")
            .textContent =
            data.cpu + "%";

        document.getElementById("memory-label")
            .textContent =
            data.memory + "%";


        document.getElementById("cpu-bar")
            .style.width =
            cpu + "%";

        document.getElementById("memory-bar")
            .style.width =
            memory + "%";


        document.getElementById("memory-available")
            .textContent =
            data.memory_available + " MB";


        document.getElementById("last-update")
            .textContent =
            new Date().toLocaleTimeString();

    }

    catch (error) {

        console.error(
            "Dashboard update failed:",
            error
        );

    }

}


updateDashboard();

setInterval(
    updateDashboard,
    2000
);

</script>


</body>

</html>
"""


class AppHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        start = time.time()

        status_code = 200

        try:

            if self.path == "/health":

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "text/plain"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()

                self.wfile.write(
                    b"OK"
                )

                REQUEST_COUNTER_VALUE[0] += 1

                REQUEST_COUNT.labels(
                    method="GET",
                    endpoint="/health",
                    status="200"
                ).inc()

                return


            if self.path == "/api/status":

                response = json.dumps(
                    get_status_data()
                ).encode("utf-8")

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "application/json"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()

                self.wfile.write(response)

                REQUEST_COUNTER_VALUE[0] += 1

                REQUEST_COUNT.labels(
                    method="GET",
                    endpoint="/api/status",
                    status="200"
                ).inc()

                return


            if self.path == "/metrics":

                metrics = generate_latest()

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    CONTENT_TYPE_LATEST
                )

                self.end_headers()

                self.wfile.write(metrics)

                REQUEST_COUNT.labels(
                    method="GET",
                    endpoint="/metrics",
                    status="200"
                ).inc()

                return


            # Simulate application processing.

            time.sleep(0.2)


            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Cache-Control",
                "no-store"
            )

            self.send_header(
                "Server",
                "Kubernetes-Monitoring-App"
            )

            self.end_headers()

            self.wfile.write(
                HTML_PAGE.encode("utf-8")
            )

            REQUEST_COUNTER_VALUE[0] += 1

            REQUEST_COUNT.labels(
                method="GET",
                endpoint="/",
                status="200"
            ).inc()


        except Exception:

            status_code = 500

            REQUEST_COUNT.labels(
                method="GET",
                endpoint=self.path,
                status="500"
            ).inc()

            raise


        finally:

            duration = time.time() - start

            REQUEST_LATENCY.labels(
                endpoint=self.path
            ).observe(duration)

            update_system_metrics()


    def log_message(self, format, *args):

        print(
            f"[{self.log_date_time_string()}] "
            f"{self.client_address[0]} "
            f"{self.command} "
            f"{self.path}"
        )


if __name__ == "__main__":

    print(
        "🚀 Kubernetes Monitoring App"
    )

    print(
        "📡 Server running on port 8000"
    )

    print(
        f"📦 Pod Hostname: "
        f"{socket.gethostname()}"
    )

    print(
        "📊 Prometheus metrics: "
        "/metrics"
    )

    server = ThreadingHTTPServer(
        ("0.0.0.0", 8000),
        AppHandler
    )

    server.serve_forever()

    #placeholder test