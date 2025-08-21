# QuantumTrades

QuantumTrades is a real-time trading web application built with Django and WebSocket channels. It supports user registration, login, logout, admin (user management), order placement, live order book updates, and trade notifications.

###Set Up instruction

###prerequisites
- Python 3.13+
- MySQL / MySQL Workbench
- Redis server (for channels layer)
- Node.js (optional)
- Git (to clone repository)

###Installation
1. Clone the repository:
    git clone <your-repo-url>
    cd quantumtrades
2. Create and activate Python virtual environment:
  - python -m venv .venv
  - source .venv/bin/activate
3. pip install -r requirements.txt
4. Start Redis server for channel layers
  -redis-server
5. Run the Django development server:
  -python manage.py runserver

###Running the Project
1. Open web browser and access http://localhost:8000
2. Register as new user or login with existing credentials.
3. Place buy or sell orders via the dashboard (if trader user).
4. Can manage user roles (if admin user) - Cannot place order
5. View live order book and recent trades with automatic real-time updates via WebSockets.
6. Receive browser notifications for completed trades.


