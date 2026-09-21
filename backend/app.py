from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
from dotenv import load_dotenv
load_dotenv()
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

app = Flask(__name__)
JWT_SECRET = os.environ.get("JWT_SECRET")

def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None

        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split()

            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            logger.warning(
                "Protected endpoint accessed without authorization token"
            )
            return jsonify({
                "error": "Authorization token is required"
            }), 401

        try:
            jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            logger.warning(
                "Expired token used to access protected endpoint"
            )
            return jsonify({
                "error": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:
            logger.warning(
                "Invalid token used to access protected endpoint"
            )
            return jsonify({
                "error": "Invalid token"
            }), 401

        return function(*args, **kwargs)

    return decorated

# Allow the React frontend to communicate with this backend
CORS(app, origins=["http://localhost:3000"])

# Configure application logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

DATABASE = "security_monitoring.db"
def init_db():
    import sqlite3

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authentication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            event_type TEXT NOT NULL,
            ip_address TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()
    
@app.before_request
def log_request():
    logger.info(
        "Request: %s %s from %s",
        request.method,
        request.path,
        request.remote_addr
    )
    
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    logger.warning(
        "HTTP error %s: %s",
        error.code,
        error.description
    )

    return jsonify({
        "error": error.description
    }), error.code


@app.errorhandler(Exception)
def handle_exception(error):
    logger.exception(
        "Unhandled application error: %s",
        error
    )

    return jsonify({
        "error": "Internal server error"
    }), 500
    

@app.route("/")
def home():
    logger.info("Home endpoint accessed")
    return jsonify({
        "message": "Security Monitoring API is running"
    })
    
def record_authentication_event(
    username: str,
    event_type: str,
    ip_address: str
) -> None:
    import sqlite3
    from datetime import datetime

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO authentication_logs
        (username, event_type, ip_address, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        username,
        event_type,
        ip_address,
        datetime.now(timezone.utc).isoformat()
    ))

    connection.commit()
    connection.close()
        
@app.route("/register", methods=["POST"])
def register():
    import sqlite3

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logger.warning(
            "Registration attempt with missing username or password"
        )

        return jsonify({
            "error": "Username and password are required"
        }), 400

    password_hash = generate_password_hash(password)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        connection.commit()

        logger.info(
            "User registered successfully: %s",
            username
        )

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except sqlite3.IntegrityError:
        logger.warning(
            "Registration attempt for existing user: %s",
            username
        )

        return jsonify({
            "error": "User already exists"
        }), 409

    finally:
        connection.close()
        
@app.route("/login", methods=["POST"])
def login():
    import sqlite3

    data = request.get_json()

    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        record_authentication_event(
            username or "unknown",
            "LOGIN_FAILURE",
            request.remote_addr or "unknown"
        )

        return jsonify({
            "error": "Username and password are required."
        }), 400

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None or not check_password_hash(
        user[0],
        password
    ):
        record_authentication_event(
            username,
            "LOGIN_FAILURE",
            request.remote_addr or "unknown"
        )

        return jsonify({
            "error": "Invalid credentials."
        }), 401

    record_authentication_event(
        username,
        "LOGIN_SUCCESS",
        request.remote_addr or "unknown"
    )

    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful.",
        "token": token
    }), 200
    
@app.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        logger.warning("Protected endpoint accessed without authorization header")
        return jsonify({
            "error": "Authorization header is required"
        }), 401

    if not auth_header.startswith("Bearer "):
        logger.warning("Protected endpoint accessed with invalid authorization format")
        return jsonify({
            "error": "Authorization header must use Bearer token"
        }), 401

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )

        username = payload.get("sub")

        if not username:
            logger.warning("Token does not contain a username")
            return jsonify({
                "error": "Invalid token"
            }), 401

        logger.info("Protected endpoint accessed by user: %s", username)

        return jsonify({
            "message": "Access granted",
            "username": username
        }), 200

    except jwt.ExpiredSignatureError:
        logger.warning("Expired token used to access protected endpoint")
        return jsonify({
            "error": "Token has expired"
        }), 401

    except jwt.InvalidTokenError:
        logger.warning("Invalid token used to access protected endpoint")
        return jsonify({
            "error": "Invalid token"
        }), 401
        
@app.route("/auth-logs", methods=["GET"])
@token_required
def get_auth_logs():
    import sqlite3

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            event_type,
            ip_address,
            timestamp
        FROM authentication_logs
        ORDER BY id DESC
    """)

    logs = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jsonify({
        "logs": logs
    }), 200
    
@app.route("/analyse-logs", methods=["GET"])
@token_required
def analyse_logs():
    import sqlite3
    from datetime import datetime, timedelta

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cutoff_time = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()

    cursor.execute("""
        SELECT
            username,
            ip_address,
            COUNT(*) AS failed_attempts
        FROM authentication_logs
        WHERE event_type = 'LOGIN_FAILURE'
        AND timestamp >= ?
        GROUP BY username, ip_address
        HAVING COUNT(*) >= 5
    """, (cutoff_time,))

    suspicious_activity = []

    for row in cursor.fetchall():
        suspicious_activity.append({
            "username": row[0],
            "ip_address": row[1],
            "failed_attempts": row[2]
        })

    connection.close()

    return jsonify({
        "suspicious_activity": suspicious_activity
    }), 200
    
@app.route("/generate-alerts", methods=["POST"])
@token_required
def generate_alerts():
    import sqlite3
    from datetime import datetime, timedelta

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cutoff_time = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()

    cursor.execute("""
        SELECT
            username,
            ip_address,
            COUNT(*) AS failed_attempts
        FROM authentication_logs
        WHERE event_type = 'LOGIN_FAILURE'
        AND timestamp >= ?
        GROUP BY username, ip_address
        HAVING COUNT(*) >= 5
    """, (cutoff_time,))

    suspicious_activity = cursor.fetchall()

    alerts_created = 0

    for username, ip_address, failed_attempts in suspicious_activity:

        cursor.execute("""
            SELECT id
            FROM threat_alerts
            WHERE username = ?
            AND ip_address = ?
            AND alert_type = ?
            AND timestamp >= ?
        """, (
            username,
            ip_address,
            "BRUTE_FORCE_LOGIN_ATTEMPT",
            cutoff_time
        ))

        existing_alert = cursor.fetchone()

        if existing_alert:
            continue

        description = (
            f"{failed_attempts} failed login attempts "
            f"detected for user '{username}'."
        )

        cursor.execute("""
            INSERT INTO threat_alerts
            (
                username,
                ip_address,
                alert_type,
                severity,
                description,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            ip_address,
            "BRUTE_FORCE_LOGIN_ATTEMPT",
            "HIGH",
            description,
            datetime.now(timezone.utc).isoformat()
        ))

        alerts_created += 1

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Threat analysis completed.",
        "alerts_created": alerts_created
    }), 200
    
@app.route("/threat-alerts", methods=["GET"])
@token_required
def get_threat_alerts():
    import sqlite3

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            ip_address,
            alert_type,
            severity,
            description,
            timestamp
        FROM threat_alerts
        ORDER BY id DESC
    """)

    alerts = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jsonify({
        "alerts": alerts
    }), 200
    
@app.route("/dashboard-stats", methods=["GET"])
@token_required
def get_dashboard_stats():
    import sqlite3

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Total threat alerts
    cursor.execute("""
        SELECT COUNT(*)
        FROM threat_alerts
    """)
    total_alerts = cursor.fetchone()[0]

    # High severity alerts
    cursor.execute("""
        SELECT COUNT(*)
        FROM threat_alerts
        WHERE severity = 'HIGH'
    """)
    high_alerts = cursor.fetchone()[0]

    # Medium severity alerts
    cursor.execute("""
        SELECT COUNT(*)
        FROM threat_alerts
        WHERE severity = 'MEDIUM'
    """)
    medium_alerts = cursor.fetchone()[0]

    # Low severity alerts
    cursor.execute("""
        SELECT COUNT(*)
        FROM threat_alerts
        WHERE severity = 'LOW'
    """)
    low_alerts = cursor.fetchone()[0]

    # Total authentication events
    cursor.execute("""
        SELECT COUNT(*)
        FROM authentication_logs
    """)
    total_authentication_events = cursor.fetchone()[0]

    # Failed login attempts
    cursor.execute("""
        SELECT COUNT(*)
        FROM authentication_logs
        WHERE event_type = 'LOGIN_FAILURE'
    """)
    failed_login_attempts = cursor.fetchone()[0]

    connection.close()

    return jsonify({
        "total_alerts": total_alerts,
        "high_alerts": high_alerts,
        "medium_alerts": medium_alerts,
        "low_alerts": low_alerts,
        "total_authentication_events": total_authentication_events,
        "failed_login_attempts": failed_login_attempts
    }), 200
        

if __name__ == "__main__":
    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
    