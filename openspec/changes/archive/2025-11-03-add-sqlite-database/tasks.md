# Implementation Tasks

## 1. Database Configuration
- [x] 1.1 Add `DATABASE_URL` setting to `src/core/config.py`
- [x] 1.2 Add database connection pool settings (pool size, timeout, etc.)
- [x] 1.3 Update `.env.template` with database configuration examples
- [x] 1.4 Fix typo in `.env.local` (fetshu → feishu)

## 2. Database Engine and Session Management
- [x] 2.1 Create `src/core/database.py` with async engine setup
- [x] 2.2 Implement async session factory using `async_sessionmaker`
- [x] 2.3 Create dependency function `get_db_session()` for FastAPI routes
- [x] 2.4 Add database initialization function `init_db()`

## 3. Base Models and Utilities
- [x] 3.1 Create `src/models/base.py` with SQLAlchemy declarative base
- [x] 3.2 Add common mixins (timestamps, primary key patterns)
- [x] 3.3 Export base classes from `src/models/__init__.py`

## 4. FastAPI Integration
- [x] 4.1 Add database startup event to `src/app.py` (initialize tables)
- [x] 4.2 Add database shutdown event to `src/app.py` (close connections)
- [x] 4.3 Verify database connection on application startup

## 5. Validation and Testing
- [x] 5.1 Run linter and formatter (`just lint`, `just fmt`)
- [x] 5.2 Start application and verify database file is created
- [x] 5.3 Check `/docs` endpoint to ensure app starts without errors
- [x] 5.4 Validate proposal with `openspec validate add-sqlite-database --strict`
