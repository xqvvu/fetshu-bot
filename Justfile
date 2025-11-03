# List all recipes
default:
    just -l

# Install dependencies
[group('setup')]
install:
    uv sync

# Install dev dependencies
[group('setup')]
install-dev:
    uv sync --all-extras

# Run the FastAPI development server
[group('dev')]
dev:
    uv run python -m server.bootstrap --reload

# Run the application (production mode)
[group('dev')]
run:
    uv run python -m server.bootstrap --no-reload

# Run bootstrap entry point (same as dev)
[group('dev')]
start:
    uv run python -m server.bootstrap

# Format code with ruff
[group('lint')]
fmt:
    uv run ruff format .

# Check code formatting without making changes
[group('lint')]
fmt-check:
    uv run ruff format --check .

# Lint code with ruff
[group('lint')]
lint:
    uv run ruff check .

# Lint and auto-fix issues
[group('lint')]
lint-fix:
    uv run ruff check --fix .

# Run all linting checks (format + lint)
[group('lint')]
check: fmt-check lint

# Format and fix all issues
[group('lint')]
fix: fmt lint-fix

# Run tests (when implemented)
[group('test')]
test:
    uv run pytest

# Run tests with coverage (when implemented)
[group('test')]
test-cov:
    uv run pytest --cov=server --cov-report=html --cov-report=term

# Clean up generated files
[group('clean')]
clean:
    rm -rf .ruff_cache
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf dist
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Update dependencies
[group('setup')]
update:
    uv lock --upgrade

# Show outdated dependencies
[group('setup')]
outdated:
    uv pip list --outdated

# ============ Web (Frontend) ============

# Install web dependencies
[group('web')]
web-install:
    cd web && bun install

# Run web development server
[group('web')]
web-dev:
    cd web && bun run dev

# Build web for production
[group('web')]
web-build:
    cd web && bun run build

# Preview web production build
[group('web')]
web-serve:
    cd web && bun run serve

# Run web tests
[group('web')]
web-test:
    cd web && bun run test

# Format web code
[group('web')]
web-fmt:
    cd web && bun run format --write

# Check web code formatting
[group('web')]
web-fmt-check:
    cd web && bun run format

# Lint web code
[group('web')]
web-lint:
    cd web && bun run lint

# Check and fix web code (format + lint)
[group('web')]
web-check:
    cd web && bun run check --write

# Run all web checks without fixing
[group('web')]
web-check-all: web-fmt-check web-lint

# Clean web build artifacts
[group('web')]
web-clean:
    cd web && rm -rf dist .vite node_modules/.vite

# ============ Combined Commands ============

# Install all dependencies (backend + web)
[group('setup')]
install-all: install web-install

# Run both backend and web in development mode (requires tmux or parallel)
[group('dev')]
dev-all:
    @echo "Starting backend and web servers..."
    @echo "Backend: http://localhost:8000"
    @echo "Web: http://localhost:3000"
    just dev & just web-dev

# Format all code (backend + web)
[group('lint')]
fmt-all: fmt web-fmt

# Check all code (backend + web)
[group('lint')]
check-all: check web-check-all

# Clean all build artifacts (backend + web)
[group('clean')]
clean-all: clean web-clean
