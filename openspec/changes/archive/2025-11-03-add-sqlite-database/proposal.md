# Add SQLite Database Proposal

## Why
The application currently lacks persistent storage, limiting its ability to store conversation history, user data, webhook events, or any other stateful information. Adding a SQLite database layer with SQLAlchemy 2.0 async ORM provides a lightweight, zero-configuration persistence solution suitable for development and small-to-medium deployments.

## What Changes
- Add database configuration to Settings (database URL, connection pooling)
- Create SQLAlchemy async engine and session management
- Implement database initialization and migration support
- Add database lifecycle hooks to FastAPI app (startup/shutdown)
- Create base models and utilities for future schema definitions
- Update `.env.template` with database configuration examples

## Impact
- **New specs**: `database-layer` (persistence infrastructure)
- **Affected specs**: `api-server` (adds database lifecycle management)
- **Affected code**:
  - `src/core/config.py` (add database settings)
  - `src/app.py` (add startup/shutdown events)
  - New files: `src/core/database.py`, `src/models/base.py`
- **Dependencies**: Uses existing `sqlalchemy>=2.0.44` and `aiosqlite>=0.21.0`
- **Configuration**: Requires `DATABASE_URL` environment variable (defaults to local SQLite file)
