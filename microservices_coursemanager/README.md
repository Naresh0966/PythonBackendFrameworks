# Course Management System - Microservices Architecture

## Overview

This project demonstrates how a monolithic Course Management System can be decomposed into independent microservices.

Instead of having one large application handling all business logic, each service is responsible for a single business domain and owns its own database.

---

# Microservices

| Service Name | Responsibility | Endpoints Owned | Database |
|--------------|---------------|-----------------|----------|
| Course Service | Manage departments and courses | /api/courses | course.db |
| Student Service | Manage students and enrollments | /api/students | student.db |
| Auth Service | User registration, login and JWT validation | /api/auth | auth.db |
| Notification Service | Email confirmations and notifications | /api/notifications | notification.db |

---

# Service Responsibilities

## 1. Course Service

Responsible for:

- Create Course
- Update Course
- Delete Course
- View Course
- Department Management

Endpoints

GET /api/courses

GET /api/courses/<id>

POST /api/courses

PUT /api/courses/<id>

DELETE /api/courses/<id>

Database

course.db

---

## 2. Student Service

Responsible for:

- Student CRUD
- Student Enrollment
- View Student

Endpoints

GET /api/students

GET /api/students/<id>

POST /api/students

PUT /api/students/<id>

DELETE /api/students/<id>

POST /api/students/<id>/enroll

Database

student.db

---

## 3. Authentication Service

Responsible for

- User Registration
- Login
- JWT Token Generation
- Token Validation

Endpoints

POST /api/auth/register

POST /api/auth/login

Database

auth.db

---

## 4. Notification Service

Responsible for

- Sending Enrollment Confirmation Emails
- Sending Notifications

Endpoints

POST /api/notifications/send

Database

notification.db

---

# Why Microservices?

Instead of one large application, each service can:

- Scale independently
- Be deployed independently
- Use its own database
- Be developed by different teams
- Fail independently

---

# Monolith vs Microservices

## Monolithic Architecture

One application

One database

Single deployment

Simple to develop

Hard to scale as the application grows

---

## Microservices Architecture

Multiple small services

Independent databases

Independent deployments

Better scalability

Better fault isolation

Easier maintenance

---

# Data Ownership

Each microservice owns its own database.

Course Service
    ↓
course.db

Student Service
    ↓
student.db

Auth Service
    ↓
auth.db

Notification Service
    ↓
notification.db

No service directly accesses another service's database.

Communication between services happens only through HTTP APIs.

---

# Communication

Student Service
        ↓ HTTP Request
Course Service
        ↓ Response
Enrollment Completed

---

# Technologies Used

- Python
- Flask
- SQLAlchemy
- SQLite
- Requests
- REST API

---

# Future Improvements

- API Gateway
- Service Discovery
- Docker
- Kubernetes
- RabbitMQ
- Kafka
- Redis
- Load Balancer
## Synchronous vs Asynchronous Communication

### Synchronous (HTTP)

- Services communicate using direct HTTP requests.
- The client waits for a response.
- Simple to implement and debug.
- If one service is unavailable, dependent requests fail.

### Asynchronous (Message Queue)

- Services communicate through a message broker such as RabbitMQ or Kafka.
- The sender does not wait for an immediate response.
- Improves scalability and fault tolerance.
- Best for email notifications, logging, payment processing, analytics, and other background tasks.

### Comparison

| Synchronous HTTP | Asynchronous Messaging |
|------------------|------------------------|
| Immediate response | Delayed/event-driven response |
| Tight coupling | Loose coupling |
| Simpler implementation | More infrastructure required |
| Fails if dependent service is down | Messages can be processed later |
