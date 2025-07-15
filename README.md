SwiftLook API - Django Backend
SwiftLook API is a Django-based backend for a lost phone tracking application. It provides features like device registration, trackable link generation, real-time location updates via WebSockets, and user authentication with JWT and Google OAuth. This README guides you through setting up the backend on a Windows system.
Features

Device management with encrypted IMEI storage
Trackable link generation for lost device tracking
Real-time location updates using Django Channels and WebSockets
Secure authentication with JWT and Google OAuth
Asynchronous email notifications using Celery
Geolocation integration with ip-api.com
PostgreSQL database for persistent storage

Prerequisites
Before setting up the project, ensure you have the following installed:

Python (3.9 or higher): Download
PostgreSQL (13 or higher): Download
Redis (3.0.504 or higher for Windows): Download
Git (optional, for version control): Download
A code editor (e.g., VS Code)
A terminal (e.g., PowerShell or Command Prompt)

You'll also need:

An email service account (e.g., Hostinger or Gmail SMTP) for sending trackable links.
(Optional) An ip-api.com account for geolocation (the free tier is used in the code).

Project Structure
phone_tracker/
├── phone_tracker/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── devices/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── tasks.py
│   ├── consumers.py
│   ├── urls.py
├── users/
│   ├── __init__.py
│   ├── models.py
│   ├── (other user-related files)
├── admin_dashboard/
│   ├── __init__.py
│   ├── (other admin-related files)
├── manage.py
├── media/
├── staticfiles/
├── .env

Setup Instructions
1. Clone or Set Up the Project
If you have a Git repository, clone it:
git clone <repository-url>
cd phone_tracker

Otherwise, create the project directory and copy the provided files (settings.py, devices/models.py, devices/views.py, devices/tasks.py, devices/consumers.py, devices/urls.py, phone_tracker/asgi.py) into the appropriate directories.
2. Create and Activate a Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
Install the required Python packages:
pip install django==5.1.1 djangorestframework==3.15.2 django-cors-headers==4.4.0 django-allauth==64.1.0 channels==4.1.0 channels-redis==4.2.0 redis==5.0.8 python-decouple==3.8 django-cryptography==1.1 celery==5.4.0 user-agents==2.2.0 requests==2.32.3

These versions ensure compatibility with the provided code.
4. Set Up Environment Variables
Create a .env file in the project root with the following content:
SECRET_KEY=your-secure-django-secret-key
DEBUG=True
IPSTACK_ACCESS_KEY=your-ipstack-key
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
DB_NAME=swiftloo_db_wj2c
DB_USER=postgres
DB_PASSWORD=qwerty
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0


Generate a secure SECRET_KEY:python -c "import secrets; print(secrets.token_hex(32))"


The code uses ip-api.com for geolocation, so IPSTACK_ACCESS_KEY is not required unless you switch to IPStack.
Update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD with your email service credentials (e.g., Hostinger or Gmail).
Adjust DB_USER, DB_PASSWORD, DB_HOST, and DB_PORT if using a different PostgreSQL setup.

5. Set Up PostgreSQL
Install PostgreSQL if not already installed. Then, create a database:

Open the PostgreSQL command line (e.g., via psql or pgAdmin).
Run:CREATE DATABASE swiftloo_db_wj2c;
CREATE USER postgres WITH PASSWORD 'qwerty';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE swiftloo_db_wj2c TO postgres;



If using a hosted database (e.g., Render), update the .env file with the provided credentials.
6. Install and Start Redis

Download Redis for Windows from GitHub (e.g., Redis-x64-3.0.504.zip).

Extract the ZIP file to a directory (e.g., C:\Redis).

Start Redis in a new terminal:
cd C:\Redis
.\redis-server.exe

If you see an error like redis-server.exe : The term 'redis-server.exe' is not recognized, ensure you're in the correct directory and use the relative path (e.g., .\redis-server.exe).

Verify Redis is running:
redis-cli ping

Output should be: PONG.


7. Apply Database Migrations
Run the following commands to set up the database schema:
python manage.py makemigrations
python manage.py migrate

Create a superuser for admin access:
python manage.py createsuperuser

8. Start Celery
Celery handles asynchronous tasks like sending emails. Open a new terminal, activate the virtual environment, and start the Celery worker:
venv\Scripts\activate
celery -A phone_tracker worker -l info

Ensure Redis is running before starting Celery.
9. Start the Django Development Server
Run the Django server:
python manage.py runserver 0.0.0.0:9090

The server will be available at http://localhost:9090. Access the admin panel at http://localhost:9090/admin/ using the superuser credentials.
10. Test the Backend

Admin Panel: Log in at http://localhost:9090/admin/ to manage users and devices.
API Endpoints:
Get a JWT token:curl -X POST http://localhost:9090/api/token/ -d "email=your_email&password=your_password"


List devices:curl -H "Authorization: Bearer your_jwt_token" http://localhost:9090/api/devices/devices/


Generate a trackable link:curl -X POST http://localhost:9090/api/devices/generate-link/ -H "Authorization: Bearer your_jwt_token" -d "{\"device_id\": 1, \"email\": \"recipient@example.com\"}"





Troubleshooting

Redis Error: If .\redis-server.exe fails, ensure you're in the Redis directory (e.g., C:\Redis). Check if Redis is installed correctly and the port 6379 is not blocked.
Celery Not Working: Verify Redis is running and the CELERY_BROKER_URL in .env is correct. Check Celery logs for errors.
Database Connection Issues: Ensure PostgreSQL is running and the .env credentials match your setup. Test with:psql -U postgres -h localhost -d swiftloo_db_wj2c


ImportError for DEFAULT_CHANNEL_LAYER: Ensure channels==4.1.0 and channels-redis==4.2.0 are installed, and no code references DEFAULT_CHANNEL_LAYER.
CORS Issues: If testing with a frontend, ensure CORS_ALLOWED_ORIGINS includes the frontend URL. For local testing, DEBUG=True allows all origins.

Security Notes

Replace the default SECRET_KEY with a secure value in production.
Use a proper SMTP service (e.g., SendGrid) for emails in production.
Set DEBUG=False and configure SECURE_SSL_REDIRECT=True in production.
Ensure CSRF_COOKIE_SECURE and SESSION_COOKIE_SECURE are True in production.

Deployment
For production deployment (e.g., on Render or Heroku):

Push the code to a GitHub repository.
Set up a PostgreSQL database and Redis instance on the hosting platform.
Update .env with production credentials.
Configure a Celery worker service:celery -A phone_tracker worker -l info


Serve static files using a CDN or cloud storage (e.g., AWS S3).
Ensure HTTPS is enabled with a valid SSL certificate.

Additional Notes

The users and admin_dashboard apps are assumed to exist. Ensure their models and views are configured correctly.
If integrating a frontend, update CORS_ALLOWED_ORIGINS with the frontend's production URL.
For enhanced security, consider adding rate limiting (e.g., django-ratelimit) and monitoring (e.g., Sentry).

For further assistance, contact the project maintainer or refer to the Django documentation.