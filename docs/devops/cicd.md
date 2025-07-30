# CI/CD Pipeline

The project uses GitHub Actions for CI/CD. The pipeline is split into two workflows:

## Continuous Integration (CI)

The CI workflow runs on every push and pull request to the `main`, `test`, and `dev` branches. It includes:

-   **Linting**: Code is checked with Ruff and formatted with Black.
-   **Type Checking**: Static type checking with mypy.
-   **Security Scanning**: Dependency scanning with Safety.
-   **Testing**: Unit and integration tests are run with pytest across Python 3.9, 3.10, and 3.11.
-   **Coverage**: Code coverage is measured and uploaded to Codecov.

## Continuous Deployment (CD)

The CD workflow runs on pushes to specific branches:

-   **`dev` → Development Environment**: Automatic deployment to the development environment.
-   **`test` → Staging Environment**: Automatic deployment to the staging environment.
-   **`main` → Production Environment**: Automatic deployment to production, with additional security checks.

## Security

The production deployment includes:

-   **Bandit**: Security scanning for Python code.
-   **Safety**: Dependency vulnerability scanning.
-   **Docker**: The bot is containerized for secure and consistent deployments.
