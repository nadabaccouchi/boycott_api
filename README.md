Boycott Products Management API
📌 Project Overview

The Boycott Products Management API is a backend web service designed to centralize and structure information about boycotted products in Tunisia and suggest available Tunisian local alternatives.
The API aims to support ethical consumption by providing reliable, organized, and easily accessible data for developers and consumers.

This project was developed as part of the IT325 – Web Services course at Tunis Business School.

🎯 Project Objectives

Centralize boycott-related product and brand information

Provide structured RESTful endpoints for easy data access

Encourage ethical consumption and support Tunisian local brands

Allow moderated community participation through reports

Demonstrate proper API design, authentication, and data validation

🛠️ Technologies Used

Backend Framework: Flask (Python)

API Architecture: RESTful API

Database: PostgreSQL

ORM: SQLAlchemy

Authentication: JWT (JSON Web Tokens)

API Documentation: Swagger / OpenAPI (Flask-Smorest)

Data Validation: Marshmallow

Version Control: Git & GitHub

🔐 Authentication & Roles

The API uses JWT-based authentication with role management:

Public users:

Can access GET endpoints (products, brands, categories)

Authenticated users:

Can submit reports about products

Admin users:

Can create, update, and delete products, brands, and categories

Can manage boycott status and alternatives

This ensures controlled access while keeping the platform informative and open.

📂 Main Features

Product, brand, and category management

Boycott status tracking

Tunisian local alternatives suggestion

Search and filtering (by name, brand, category)

User reporting system with moderation logic

Clear and documented API endpoints

🧩 API Structure

The project follows a clean and modular structure:

models/ – Database models

resources/ – API endpoints (routes)

schemas/ – Data validation and serialization

auth/ – Authentication and authorization logic

app.py – Application entry point

📖 API Documentation

All endpoints are documented using Swagger UI, allowing easy testing and exploration of the API:

http://localhost:5000/swagger-ui

⚠️ Challenges & Limitations

Boycott data accuracy depends on available sources and user reports

Availability of local alternatives varies by product category

The project focuses on backend functionality, with frontend integration considered as a future enhancement

🚀 Future Improvements

Full frontend application for public users and administrators

Advanced data verification workflows

Analytics on boycott trends and user engagement

Integration with external data sources

👩‍💻 Author

Nada Baccouchi
Business Analytics – Information Technology
Tunis Business School
Academic Year: 2025–2026
