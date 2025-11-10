# OAuth2 Authorization Server

A FastAPI-based OAuth2 authorization server that handles user authentication, token issuance, and access policy enforcement.

## Architecture

```mermaid
graph TD
    Client[Client Application] -- HTTP Request --> API[FastAPI Application]
    
    subgraph API Service
        API -- Authentication --> Auth[Authentication Service]
        API -- User Management --> UserMgmt[User Management]
        API -- Role Management --> RoleMgmt[Role Management]
        
        Auth -- Verify Token --> Security[Security Layer]
        Auth -- Get User --> Database
        UserMgmt -- CRUD Operations --> Database
        RoleMgmt -- Manage Roles --> Database
        
        Security -- JWT Token --> JWT[JWT Handler]
        Security -- Password Hash --> BCrypt[Password Hasher]
    end
    
    subgraph Data Layer
        Database[(SQLite Database)]
        Database -- Users Table --> Users[(Users)]
        Database -- Roles Table --> Roles[(Roles)]
        Database -- UserRoles Table --> UserRoles[(User Roles)]
    end
    
    subgraph Models & Schemas
        Users -- SQLAlchemy Models --> SQLModels[SQLAlchemy Models]
        Roles -- SQLAlchemy Models --> SQLModels
        UserRoles -- SQLAlchemy Models --> SQLModels
        API -- Pydantic Schemas --> Schemas[Pydantic Schemas]
    end
```

## System Components

1. **API Layer**
   - FastAPI application handling HTTP requests
   - Route handlers for authentication, users, and roles
   - Request/response validation using Pydantic schemas

2. **Security Layer**
   - JWT token generation and validation
   - Password hashing with BCrypt
   - Role-based access control (RBAC)

3. **Data Layer**
   - SQLite database for persistent storage
   - SQLAlchemy ORM for database operations
   - Three main tables: Users, Roles, and UserRoles

4. **Models & Schemas**
   - SQLAlchemy models for database operations
   - Pydantic schemas for request/response validation
   - Data transformation and validation logic

## Features

- User authentication with username/password
- JWT token issuance and validation
- Role-based access control (RBAC)
- SQLite database backend
- Poetry dependency management
- API documentation with OpenAPI/Swagger

## Installation

1. Make sure you have Poetry installed:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

## Usage

Start the server:
```bash
poetry run start
```

The server will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints and Examples

### Authentication

#### Get Access Token
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -F "username=your_username" \
  -F "password=your_password"
```

### Users

#### Create New User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "strongpassword",
    "roles": ["user"]
  }'
```

#### List All Users (Admin Only)
```bash
curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer your_access_token"
```

#### Get Current User Info
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer your_access_token"
```

#### Get Specific User Info (Admin or Self)
```bash
curl -X GET "http://localhost:8000/users/username" \
  -H "Authorization: Bearer your_access_token"
```

#### Update User (Admin or Self)
```bash
curl -X PUT "http://localhost:8000/users/username" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "password": "newpassword",
    "is_active": true
  }'
```

#### Delete User (Admin Only)
```bash
curl -X DELETE "http://localhost:8000/users/username" \
  -H "Authorization: Bearer your_access_token"
```

### Roles

#### Update User Roles (Admin Only)
```bash
curl -X PUT "http://localhost:8000/roles/username" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["admin", "user"]
  }'
```

## Response Examples

### Successful Authentication
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

### User Response
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "is_active": true,
  "roles": ["user", "admin"]
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

## Role-Based Access Control

The server implements role-based access control with the following default roles:
- `admin`: Full access to all endpoints
- `user`: Access to personal information and limited operations
- `manager`: Custom role for specific access patterns

Certain operations require specific roles:
- Listing all users: Requires `admin` role
- Updating user roles: Requires `admin` role
- Deleting users: Requires `admin` role
- Updating user information: Requires `admin` role or self-modification
- Viewing user details: Requires `admin` role or self-viewing

## Development

To run the server in development mode with auto-reload:
```bash
poetry run start
```

## Security Notes

- In production, replace the default secret key with a secure one
- Use HTTPS in production
- Implement rate limiting for production use
- Consider adding password complexity requirements
- Review and adjust token expiration times as needed

## Project Structure

```
auth_server/
    auth_server/
        database/           # Database configuration and sessions
            __init__.py
            db.py
        security/          # Security and authentication
            __init__.py
            auth.py
        models/            # SQLAlchemy models
            __init__.py
            role.py
            user_role.py
            user.py
        routers/           # API routes
            __init__.py
            auth.py
            roles.py
            users.py
        schemas/           # Pydantic schemas
            __init__.py
            role.py
            user.py
```

## Support & Contact

For support requests, bug reports, or feature suggestions, please contact:

### Technical Support
- Email: v.cse59@gmail.com
- Response Time: 24-48 hours
- Hours: Monday-Friday, 9:00 AM - 5:00 PM (UTC)

### Security Issues
For security-related concerns or vulnerability reports:
- Email: v.cse59@gmail.com

### Documentation
For documentation improvements or suggestions:
- GitHub Issues: [Create an issue](https://github.com/your-organization/auth-server/issues)
- Documentation Wiki: [Auth Server Wiki](https://github.com/your-organization/auth-server/wiki)

### Commercial Support
For enterprise support and custom development:
- Email: v.cse59@gmail.com