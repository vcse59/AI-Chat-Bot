MCP Monorepo
============

This repository (MCP) contains multiple projects and prototypes. The primary project in this workspace is the "Authentication-Authorization" service which implements an OAuth2 / JWT-based authorization server built with FastAPI.

Directory of interest
---------------------
- `Authentication-Authorization/` — contains the Authorization Server project, including the FastAPI app under `auth_server/` and a `pyproject.toml` for dependency management. See `Authentication-Authorization/README.md` for full details and configuration.

Quick start (Authentication-Authorization)
-----------------------------------------
1. Change to the subproject directory:

   ```cmd
   cd Authentication-Authorization
   ```

2. Install dependencies (Poetry):

   ```cmd
   poetry install
   ```

3. Start the service (development):

   ```cmd
   poetry run start
   ```

4. Open the API docs in your browser:

   - http://localhost:8000/docs

Notes
-----
- If the subproject uses a different install or run command, follow the instructions in `Authentication-Authorization/README.md`.
- The service uses SQLite by default (file-based DB). Back up `auth.db` before destructive testing.

Support & Contact
-----------------
For project-specific support see `Authentication-Authorization/README.md`. Placeholder contacts:

- Email: support@example.com
- Security: security@example.com

Contributing
------------
Contributions are welcome. Please open a GitHub issue or a pull request against the `main` branch.

Project Structure
-----------------
```
Authentication-Authorization/
    README.md
    pyproject.toml
    auth_server/
        README.md
        auth_server/
            ... (FastAPI app)
```
