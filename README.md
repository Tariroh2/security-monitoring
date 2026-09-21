# Security Monitoring Application

## Overview

This project is a full-stack Security Monitoring application developed using a Python Flask backend and a React TypeScript frontend.

The application allows security analysts to register and authenticate, access protected resources, monitor authentication activity, analyse suspicious login behaviour, and view threat alerts through a security monitoring dashboard.

## Objectives

The application was developed to demonstrate:

- User registration and authentication
- Secure password storage
- JWT-based authentication
- Protected API endpoints
- Authentication event logging
- Suspicious login activity analysis
- Threat alert generation
- Security monitoring dashboard
- React and TypeScript frontend development
- Communication between a frontend and backend through REST APIs

## Technologies Used

### Backend

- Python 3
- Flask
- Flask-CORS
- PyJWT
- SQLite
- Werkzeug password hashing
- Python logging
- python-dotenv

### Frontend

- React
- TypeScript
- React Router
- Vite
- CSS

## Main Features

### 1. User Registration

Users can create an account through the registration page.

Passwords are securely hashed before being stored in the database.

### 2. User Login

Registered users can log in using their username and password.

Successful authentication returns a JWT token which is stored by the frontend and used when accessing protected endpoints.

### 3. Protected Routes

Protected backend endpoints require an authentication token in the following format:

    Authorization: Bearer <token>

The backend verifies the JWT before allowing access.

### 4. Authentication Logging

The application records authentication events including:

- LOGIN_SUCCESS
- LOGIN_FAILURE

Each event records information such as:

- Username
- Event type
- IP address
- Timestamp

### 5. Threat Detection

The application analyses authentication logs for suspicious activity.

The current detection rule identifies repeated failed login attempts for the same username and IP address within a defined time period.

### 6. Threat Alerts

Detected suspicious activity can generate stored threat alerts.

Each alert contains:

- Username
- IP address
- Alert type
- Severity
- Description
- Timestamp

### 7. Security Dashboard

The dashboard provides an overview of the monitoring system, including:

- Total alerts
- High-severity alerts
- Medium-severity alerts
- Low-severity alerts
- Total authentication events
- Failed login attempts

Threat alerts can also be filtered by severity.

### 8. Authentication Log Viewer

A dedicated page allows analysts to review authentication activity recorded by the system.

### 9. Logout

Users can log out of the application. The authentication token is removed from browser storage and the user is redirected to the login page.

## Project Structure

    security-monitoring/
    │
    ├── backend/
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── .env
    │   ├── security_monitoring.db
    │   └── app.log
    │
    ├── frontend/
    │   ├── src/
    │   ├── package.json
    │   └── vite.config.ts
    │
    ├── .gitignore
    └── README.md

The database, log file, environment file, virtual environment and Node dependencies are excluded from version control through `.gitignore`.

## Installation and Setup

### Backend

Open PowerShell and navigate to the backend directory:

    cd security-monitoring\backend

Activate the Python virtual environment:

    ..\venv\Scripts\Activate.ps1

Install the required Python packages:

    pip install -r requirements.txt

Create a `.env` file in the backend directory and add:

    JWT_SECRET=your-long-random-secret

Start the Flask server:

    python app.py

The backend runs on:

    http://127.0.0.1:5000

### Frontend

Open another PowerShell window and navigate to the frontend directory:

    cd security-monitoring\frontend

Install the frontend dependencies:

    npm install

Start the React development server:

    npm run dev

The frontend runs on:

    http://localhost:3000

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/register` | Register a new user |
| POST | `/login` | Authenticate a user and return a JWT |
| GET | `/protected` | Test protected access |
| GET | `/auth-logs` | Retrieve authentication logs |
| GET | `/analyse-logs` | Analyse authentication activity |
| POST | `/generate-alerts` | Generate threat alerts |
| GET | `/threat-alerts` | Retrieve stored threat alerts |
| GET | `/dashboard-stats` | Retrieve dashboard statistics |

Protected endpoints require a valid JWT.

## Security Features

The application includes:

- Password hashing
- JWT authentication
- Protected API endpoints
- CORS configuration
- Authentication event logging
- Suspicious login detection
- Threat alert storage
- Environment-based JWT secret configuration
- Error handling
- Input validation for authentication requests

## Testing

The application was tested for:

- Successful user registration
- Duplicate user registration
- Successful login
- Invalid login credentials
- JWT-protected endpoints
- Authentication event recording
- Failed login detection
- Threat alert generation
- Dashboard statistics
- Threat alert display
- Severity filtering
- Authentication log viewing
- Logout
- Invalid and expired token handling

## Future Improvements

Possible future improvements include:

- Role-based access control
- More advanced threat detection rules
- Real-time alert updates
- Additional security monitoring dashboards
- Email or notification-based alerts
- Integration with external security information and event management systems
- More detailed incident investigation capabilities

## Author

Tariro Mavhuve Cybersecurity and Forensic Audit Student

## Project Purpose

This project was developed as a practical full-stack cybersecurity and security monitoring application demonstrating backend API development, authentication, logging, threat detection, database management and frontend dashboard development.