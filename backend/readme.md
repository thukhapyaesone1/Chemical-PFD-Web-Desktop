# Django API Project

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.x-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

Backend API for a **Chemical Process Flow Diagram (PFD)** system built with **Django + Django REST Framework**, featuring **JWT authentication**, **project CRUD**, and **component management**.

---

## Table of Contents

- [Chemical PFD Django Backend API](#chemical-pfd-django-backend-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Setup](#setup)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Create a virtual environment](#2-create-a-virtual-environment)
    - [3. Activate the virtual environment](#3-activate-the-virtual-environment)
    - [4. Install dependencies](#4-install-dependencies)
    - [5. Run migrations](#5-run-migrations)
    - [6. Create a superuser (required for admin)](#6-create-a-superuser-required-for-admin)
  - [Running the Project](#running-the-project)
  - [Authentication](#authentication)
  - [API Documentation](#api-documentation)
    - [1. Hello World](#1-hello-world)
    - [2. Authentication Endpoints](#2-authentication-endpoints)
      - [2.1 Register User](#21-register-user)
      - [2.2 Login User](#22-login-user)
      - [2.3 Refresh Access Token](#23-refresh-access-token)
    - [3. Components API](#3-components-api)
      - [3.1 List \& Create Components](#31-list--create-components)
    - [4. Projects API](#4-projects-api)
      - [4.1 List \& Create Projects](#41-list--create-projects)
      - [4.2 Project Detail \& Update \& Delete](#42-project-detail--update--delete)
  - [Admin Component Import](#admin-component-import)
  - [Authentication Flow Summary](#authentication-flow-summary)

---

## Features

- JWT Authentication (register, login, refresh)
- RESTful API using Django REST Framework
- CRUD for Projects with nested ProjectComponents
- List, fetch, and create Components
- Bulk component import via Django Admin (ZIP upload)
- SVG & PNG media support
- Test coverage for admin utilities and APIs

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create a virtual environment

```bash
python -m venv env
```

### 3. Activate the virtual environment

**Windows**

```bash
env\Scripts\activate
```

**Linux / macOS**

```bash
source env/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (required for admin)

```bash
python manage.py createsuperuser
```

---

## Running the Project

```bash
python manage.py runserver
```

Access the API at:

```
http://127.0.0.1:8000/api/
```

---

## Authentication

This project uses **JWT authentication**.

Include the access token in request headers:

```
Authorization: Bearer <access_token>
```

---

## API Documentation

### 1. Hello World

**Endpoint:** `/api/hello/`  
**Method:** `GET`  

**Description:** Test endpoint to check if API is working.

**Response Example:**

```json
{
  "message": "Hello from DRF!"
}
```

---

### 2. Authentication Endpoints

#### 2.1 Register User

**Endpoint:** `/api/auth/register/`  
**Method:** `POST`  

**Request Body:**

```json
{
  "username": "your_username",
  "email": "your_email@example.com",
  "password": "your_password"
}
```

**Response Example:**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 3,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

**Status Code:** `201 Created`

---

#### 2.2 Login User

**Endpoint:** `/api/auth/login/`  
**Method:** `POST`  

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response Example:**

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

**Status Code:** `200 OK`

---

#### 2.3 Refresh Access Token

**Endpoint:** `/api/auth/refresh/`  
**Method:** `POST`  

**Request Body:**

```json
{
  "refresh": "<refresh_token>"
}
```

**Response Example:**

```json
{
  "access": "<new_access_token>"
}
```

**Status Code:** `200 OK`

---

### 3. Components API

#### 3.1 List & Create Components

**Endpoint:** `/api/components/`  
**Method:** `GET` / `POST`  

**GET Response Example:**

```json
{
  "components": [
    {
      "id": 1,
      "s_no": "101",
      "parent": "General",
      "name": "Insulation/Tracing",
      "legend": "",
      "suffix": "",
      "object": "Insulation",
      "svg": null,
      "png": null,
      "svg_url": null,
      "png_url": null,
      "grips": ""
    }
  ]
}
```

**POST Request Example:**

```json
# Form Data
{
  "s_no": "301",
  "parent": "Piping",
  "name": "Inflow Line",
  "legend": "",
  "suffix": "",
  "object": "InflowLine",
  "svg": "<file>",
  "png": "<file>",
  "grips" : ""
}
```

**POST Response Example:**

```json
{
    "id": 2,
    "s_no": "301",
    "parent": "Piping",
    "name": "Inflow Line",
    "legend": "",
    "suffix": "",
    "object": "InflowLine",
    "svg": "<file>",
    "png": "<file>"
}
```

---

### 4. Projects API

#### 4.1 List & Create Projects

**Endpoint:** `/api/project/`  
**Method:** `GET` / `POST`  

**GET Response Example:**

```json
{
  "status": "success",
  "projects": [
    {
      "id": 1,
      "name": "Project A",
      "description": "Test project"
    }
  ]
}
```

**POST Request Example:**

```json
{
  "name": "Project B",
}
```

**POST Response Example:**

```json
{
  "message": "Project created",
  "project": {
    "id": 2,
    "name": "Project B"
  }
}
```

---

#### 4.2 Project Detail & Update & Delete

**Endpoint:** `/api/project/<id>/`  
**Method:** `GET` / `PUT` / `DELETE`

**GET Response Example:**

```json
{
  "status": "success",
  "project": {
    "id": 1,
    "name": "Project A",
    "description": "Test project",
    "components": [
      {
        "id": 1,
        "component_id": 101,
        "component_unique_id": "uuid123",
        "connections": []
      }
    ]
  }
}
```

**PUT Request Example (Update Components):**

```json
 {
        "id": 2,
        "name": "demo project 2 update",
        "created_at": "2025-12-12T04:19:48.043208Z",
        "user": 2,
        "components": [
            {
                "component_id" : "1342",
                "component_unique_id": "com5",
                "connections": [
                    "com4",
                    "com2"
                ]
            },
             {
                "component_id" : "1347",
                "component_unique_id": "com5",
                "connections": [
                    "com4",
                    "com2"
                ]
            }
        ]
    }
```

**PUT Response Example:**

```json
{
    "status": "success",
    "message": "Project updated successfully",
    "project": {
        "id": 2,
        "name": "demo project 2 update",
        "created_at": "2025-12-12T04:19:48.043208Z",
        "user": 2,
        "components": [
            {
                "id": 1342,
                "name": "Liquid Flow",
                "svg": null,
                "png": null,
                "legend": "",
                "suffix": "",
                "component_unique_id": "com5",
                "connections": [
                    "com4",
                    "com2"
                ]
            },
            {
                "id": 1347,
                "name": "Connecting Line",
                "svg": null,
                "png": null,
                "legend": "",
                "suffix": "",
                "component_unique_id": "com5",
                "connections": [
                    "com4",
                    "com2"
                ]
            }
        ]
    }
}
```

**DELETE Response Example:**

```json
{
    "status": "success",
    "message": "Project deleted successfully"
}
```

**Not Found Response Example:**

```json
{
    "status": "error",
    "message": "Project not found"
}
```

---

## Admin Component Import

Components can be bulk imported via Django Admin using a ZIP file.

**ZIP structure:**

```
components/
├── components.csv
├── svg/
│   ├── component_1.svg
│   └── component_2.svg
└── png/
    ├── component_1.png
    └── component_2.png
```

1. Login to Django Admin (`/admin/`)  
2. Go to **Components** → **Upload ZIP**  
3. Upload the ZIP following the structure above  

---

## Authentication Flow Summary

1. **Register** → create user  
2. **Login** → receive access & refresh tokens  
3. **Access protected endpoints** → include `Authorization: Bearer <access>` header  
4. **Refresh** → get new access token using refresh token  
