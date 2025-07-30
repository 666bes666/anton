# Contributing

Thank you for your interest in contributing to the Discord Daily Message Bot!

## Development Setup

1.  **Clone the repository**: `git clone https://github.com/666bes666/anton.git`
2.  **Set up the environment**: Install Python 3.9+ and create a virtual environment.
3.  **Install dependencies**: `pip install -r requirements.txt`
4.  **Run the tests**: `pytest`
5.  **Install pre-commit hooks**: `pre-commit install`

## Branching Strategy

We use a three-branch development strategy:

-   **`main`**: The production branch. Code merged here is automatically deployed to production.
-   **`test`**: The staging branch. Code is tested here before being merged to main.
-   **`dev`**: The development branch. All new features and bug fixes are merged here first.

## Making Changes

1.  Create a feature branch from `dev`: `git checkout -b feature/my-new-feature`
2.  Make your changes and write tests.
3.  Run the full test suite: `pytest`
4.  Create a pull request to merge your branch into `dev`.

## Code Style

The project uses the following tools for code quality:

-   **Black**: For code formatting.
-   **Ruff**: For linting.
-   **mypy**: For type checking.

These are enforced by pre-commit hooks and CI.
