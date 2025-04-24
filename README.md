# Task Management System

## Overview
The Task Management System is a Django-based application designed to manage projects, tasks, and comments with role-based access control. It includes features like user authentication, search, filtering, and caching for efficient data handling.

---

## API Endpoints

### **Authentication**
- **POST /api/auth/signup/**
  - **Description**: Register a new user.
  - **Request Body**:
    ```json
    {
      "email": "string",
      "password": "string",
      "name": "string",
      "role": "string"  // Admin, Project Manager, Developer, Client
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "email": "string",
      "name": "string",
      "role": "string"
    }
    ```

- **POST /api/auth/login/**
  - **Description**: Log in a user and retrieve JWT tokens.
  - **Request Body**:
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```
  - **Response**:
    ```json
    {
      "refresh": "string",
      "access": "string",
      "user": {
        "id": 1,
        "email": "string",
        "name": "string",
        "role": "string"
      },
      "message": "Login successful!"
    }
    ```

### **Projects**
- **GET /api/projects/**
  - **Description**: Retrieve a list of projects with search and filtering options.
  - **Query Parameters**:
    - `search`: Search by name or description.
    - `manager`: Filter by manager ID.
    - `members`: Filter by member ID.
  - **Response**:
    ```json
    {
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 1,
          "name": "string",
          "description": "string",
          "start_date": "YYYY-MM-DD",
          "end_date": "YYYY-MM-DD",
          "manager": 1,
          "members": [1, 2]
        }
      ]
    }
    ```

- **POST /api/projects/**
  - **Description**: Create a new project.
  - **Request Body**:
    ```json
    {
      "name": "string",
      "description": "string",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "members": [1, 2]
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "manager": 1,
      "members": [1, 2]
    }
    ```

### **Tasks**
- **GET /api/tasks/**
  - **Description**: Retrieve a list of tasks with search and filtering options.
  - **Query Parameters**:
    - `search`: Search by title or description.
    - `status`: Filter by task status.
    - `priority`: Filter by task priority.
    - `project`: Filter by project ID.
    - `assigned_to`: Filter by assigned user ID.
  - **Response**:
    ```json
    {
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 1,
          "title": "string",
          "description": "string",
          "status": "string",
          "priority": "string",
          "project": 1,
          "assigned_to": 1
        }
      ]
    }
    ```

- **POST /api/tasks/**
  - **Description**: Create a new task.
  - **Request Body**:
    ```json
    {
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "project": 1,
      "assigned_to": 1
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "status": "string",
      "priority": "string",
      "project": 1,
      "assigned_to": 1
    }
    ```

### **Comments**
- **GET /api/comments/**
  - **Description**: Retrieve a list of comments.
  - **Response**:
    ```json
    {
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 1,
          "content": "string",
          "author": 1,
          "task": 1,
          "project": null
        }
      ]
    }
    ```

- **POST /api/comments/**
  - **Description**: Create a new comment.
  - **Request Body**:
    ```json
    {
      "content": "string",
      "task": 1
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "content": "string",
      "author": 1,
      "task": 1,
      "project": null
    }
    ```

---

## Database Schema

### **User**
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `password`: String
- `name`: String
- `role`: String (Admin, Project Manager, Developer, Client)

### **Project**
- `id`: Integer (Primary Key)
- `name`: String
- `description`: String
- `start_date`: Date
- `end_date`: Date
- `manager`: Foreign Key (User)
- `members`: Many-to-Many (User)

### **Task**
- `id`: Integer (Primary Key)
- `title`: String
- `description`: String
- `status`: String (Pending, In Progress, Completed)
- `priority`: String (Low, Medium, High)
- `project`: Foreign Key (Project)
- `assigned_to`: Foreign Key (User)

### **Comment**
- `id`: Integer (Primary Key)
- `content`: String
- `author`: Foreign Key (User)
- `task`: Foreign Key (Task)
- `project`: Foreign Key (Project, Nullable)

---

## Authentication Mechanisms

### **JWT Authentication**
- The application uses JSON Web Tokens (JWT) for authentication.
- **Access Token**: Short-lived token for accessing protected resources.
- **Refresh Token**: Long-lived token for obtaining new access tokens.

### **How to Authenticate**
1. Obtain tokens by logging in via `/api/auth/login/`.
2. Use the `access` token in the `Authorization` header for subsequent requests:
   ```
   Authorization: Bearer <ACCESS_TOKEN>
   ```
3. Refresh the `access` token using the `refresh` token when it expires.

---

## Future Development
- Add more granular permissions for specific actions.
- Implement notifications for task updates.
- Enhance reporting and analytics for project progress.

---

## Setup Instructions
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run the development server:
   ```bash
   python manage.py runserver
   ```
5. Access the application at `http://127.0.0.1:8000/`.

---
