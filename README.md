# Authentication, Authorization & Security modules

![CI](https://github.com/vcse59/MCP/actions/workflows/ci.yml/badge.svg) ![License](https://img.shields.io/badge/license-MIT-blue) ![python](https://img.shields.io/badge/python-3.12%2B-brightgreen)

This is a monorepo for authentication, authorization, and security modules.

This repository contains multiple projects and prototypes. The primary project in this workspace is the "Authentication-Authorization" service, which implements an OAuth2 / JWT-based authorization server built with FastAPI.

Directory of interest
---------------------
- `Authentication-Authorization/` — contains the Authorization Server project, including the FastAPI app under `auth_server/` and a `pyproject.toml` for dependency management. See `Authentication-Authorization/README.md` for full details and configuration.

Quick Start (Authentication-Authorization)
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

- Email: v.cse59@gmail.com
- Security: v.cse59@gmail.com

Contributing
------------
Contributions are welcome — thank you! To contribute, please follow this short checklist:

- Fork the repository and create a feature branch (use prefixes like `feat/`, `fix/`, or `chore/`).
- Keep changes small and focused. Add tests for new behavior where applicable.
- Run linters and tests locally before submitting a PR.
- Open a Pull Request against the `main` branch with a clear title and description. Link any relevant issues.

For larger design changes, open an Issue first to discuss the proposal.

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

Links
-----
- Subproject README: `Authentication-Authorization/README.md`
- FastAPI docs: https://fastapi.tiangolo.com/
- OpenAPI / Swagger UI (when running locally): http://localhost:8000/docs

See `CONTRIBUTING.md` for contribution guidelines and PR templates.
