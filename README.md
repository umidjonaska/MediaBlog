# E-Commerce Platform

A small e-commerce application built with **FastAPI**.

I started this project to learn how a production-style backend is organized. Instead of putting everything into a single file, I separated the application into routes, services, repositories, models and schemas.

Customers can browse products and place orders either through the website or using a Telegram bot. Every order is stored in PostgreSQL, and administrators are notified automatically. The project also includes Docker support, JWT authentication, Redis, and asynchronous background tasks using FastAPI's `BackgroundTasks`.

---

## Features

- JWT authentication
- User registration and login
- Product management
- Media upload and local file storage
- Place orders through the website
- Place orders through the Telegram bot
- Automatic order notifications for administrators
- RESTful API
- Swagger API documentation
- PostgreSQL database
- Docker & Docker Compose support
- Alembic database migrations
- Background tasks using FastAPI

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT |
| Database Migration | Alembic |
| Cache | Redis |
| Background Tasks | FastAPI BackgroundTasks |
| Telegram Bot | Aiogram |
| Containerization | Docker & Docker Compose |
| Frontend | HTML, CSS, JavaScript |

---

## Project Structure

```text
MediaBlog/
├── app/ # Main FastAPI backend application
│ ├── main.py # Application entry point
│ ├── api.py # API router configuration
│ ├── deps.py # Dependency injection
│ │
│ ├── auth/ # Authentication module
│ │ ├── login.py # Login and JWT authentication logic
│ │ ├── schema.py # Authentication schemas
│ │ └── services.py # Authentication services
│ │
│ ├── core/ # Core application settings
│ │ ├── config.py # Environment configuration
│ │ ├── base.py # Base classes
│ │ ├── exception.py # Custom exceptions
│ │ └── redis_cli.py # Redis client configuration
│ │
│ ├── database/ # Database connection
│ │ └── database.py
│ │
│ ├── models/ # SQLAlchemy database models
│ │ ├── user.py
│ │ ├── post.py
│ │ ├── comment.py
│ │ ├── media.py
│ │ └── order.py
│ │
│ ├── schemas/ # Pydantic request/response schemas
│ │ ├── user.py
│ │ ├── post.py
│ │ ├── comment.py
│ │ ├── media.py
│ │ └── order.py
│ │
│ ├── repositories/ # Database access layer
│ │ ├── user.py
│ │ ├── post.py
│ │ ├── comment.py
│ │ ├── media.py
│ │ └── order.py
│ │
│ ├── services/ # Business logic layer
│ │ ├── user.py
│ │ ├── post.py
│ │ ├── comment.py
│ │ ├── media.py
│ │ └── order.py
│ │
│ ├── routes/ # API endpoints
│ │ ├── user.py
│ │ ├── post.py
│ │ ├── comment.py
│ │ ├── media.py
│ │ └── order.py
│ │
│ ├── utils/ # Helper functions
│ │ ├── file.py
│ │ ├── media.py
│ │ ├── pagination.py
│ │ └── slack.py
│ │
│ └── scripts/
│ └── create_superadmin.py # Create admin user script
│
├── bot/ # Telegram bot application
│ ├── main.py
│ ├── config.py
│ │
│ ├── handlers/ # Telegram message handlers
│ ├── keyboards/ # Telegram keyboards
│ ├── services/ # API communication services
│ └── states/ # FSM states
│
├── frontend/ # Simple frontend interface
│ ├── index.html
│ ├── login.html
│ ├── post.html
│ │
│ ├── admin/
│ │ └── orders.html
│ │
│ └── assets/
│ ├── css/
│ │ └── style.css
│ └── js/
│ ├── api.js
│ ├── auth.js
│ ├── blog.js
│ ├── login.js
│ └── post.js
│
├── migrations/ # Alembic database migrations
│ ├── env.py
│ └── versions/
│ ├── initial_schema.py
│ ├── add_superadmin_role.py
│ ├── add_orders_table.py
│ └── soft_delete_migration.py
│
├── tests/ # Automated tests
│ ├── conftest.py
│ ├── test_main.py
│ │
│ ├── auth/
│ ├── repositories/
│ ├── routes/
│ ├── services/
│ └── utils/
│
├── media/ # Uploaded media files
│ └── image/
│
├── Dockerfile
├── docker-compose.yml # Docker services configuration
├── requirements.txt # Python dependencies
├── alembic.ini # Alembic configuration
├── pytest.ini # Pytest configuration
├── .env.example # Environment variables template
└── README.md
```

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/umidjonaska/MediaBlog.git
cd MediaBlog
```

---

## Environment Variables

Create a `.env` file based on `.env.example`.

---

## Run with Docker

Build and start the application:

```bash
docker compose up --build
```

This command will:

- Start PostgreSQL
- Start Redis
- Apply Alembic migrations
- Start the FastAPI application
- Start the Telegram bot

---

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Start the application:

```bash
uvicorn app.api:app --reload
```

---

## API Documentation

Swagger UI is available at:

```
Backend:
http://localhost:8000/docs
Frontend:
http://localhost:5500
```

---

## Telegram Bot

The Telegram bot allows customers to place orders without visiting the website.

The bot asks the customer for:

- Product
- Quantity
- Customer name
- Phone number

After the order is submitted:

- The order is saved to PostgreSQL.
- Administrators receive a notification.
- The order becomes available in the web application.

---

## Future Improvements

Some features I plan to add in the future:

- Shopping cart
- Product categories
- Order status tracking
- Admin dashboard
- Better frontend UI
- Improve test coverage
- GitHub Actions for CI/CD
- Deployment configuration

---

## Author

**Umidjon Askaraliev**

I'm currently learning backend development with Python and FastAPI. This project is part of my portfolio and reflects my approach to building backend applications using a layered architecture and modern development tools.

GitHub: https://github.com/umidjonaska

---

## License

This project is licensed under the MIT License.