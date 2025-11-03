# database-layer Specification

## Purpose
Provides persistent storage infrastructure for the Feishu bot application using SQLAlchemy 2.0 async ORM with SQLite database. This layer manages database connections, sessions, schema initialization, and provides base models and mixins for application data persistence. The implementation supports easy migration to other databases (PostgreSQL, MySQL) in the future.
## Requirements
### Requirement: Database Configuration
The system SHALL provide database configuration settings loaded from environment variables.

#### Scenario: Database URL configuration
- **WHEN** the application loads configuration
- **THEN** it SHALL read `DATABASE_URL` from environment variables
- **AND** it SHALL default to `sqlite+aiosqlite:///./feishu-bot.sqlite` if not specified
- **AND** the URL SHALL support SQLite and other SQLAlchemy-compatible databases

#### Scenario: Connection pool settings
- **WHEN** database configuration is initialized
- **THEN** it SHALL provide connection pool settings (pool size, timeout)
- **AND** these settings SHALL be configurable via environment variables
- **AND** default values SHALL be suitable for development and small production workloads

### Requirement: Async Database Engine
The system SHALL provide an async SQLAlchemy engine for database operations.

#### Scenario: Engine initialization
- **WHEN** the database module is imported
- **THEN** it SHALL create an async SQLAlchemy engine using the configured DATABASE_URL
- **AND** the engine SHALL use the aiosqlite driver for SQLite URLs
- **AND** the engine SHALL support connection pooling and echo mode for debugging

#### Scenario: Engine disposal
- **WHEN** the application shuts down
- **THEN** it SHALL properly dispose of the database engine
- **AND** all active connections SHALL be closed gracefully

### Requirement: Async Session Factory
The system SHALL provide an async session factory for creating database sessions.

#### Scenario: Session factory creation
- **WHEN** the database is initialized
- **THEN** it SHALL create an `async_sessionmaker` bound to the engine
- **AND** sessions SHALL have autocommit disabled
- **AND** sessions SHALL have autoflush enabled
- **AND** sessions SHALL expire on commit by default

#### Scenario: Dependency injection
- **WHEN** a FastAPI route requires a database session
- **THEN** it SHALL use the `get_db_session()` dependency function
- **AND** the session SHALL be automatically closed after the request completes
- **AND** exceptions SHALL trigger session rollback

### Requirement: Database Initialization
The system SHALL initialize the database schema on application startup.

#### Scenario: Schema creation
- **WHEN** the `init_db()` function is called on startup
- **THEN** it SHALL create all tables defined in the declarative base
- **AND** table creation SHALL be idempotent (safe to run multiple times)
- **AND** existing tables SHALL not be dropped or modified

#### Scenario: Startup verification
- **WHEN** the application starts
- **THEN** it SHALL verify database connectivity
- **AND** initialization errors SHALL prevent application startup
- **AND** error messages SHALL include connection details for debugging

### Requirement: Declarative Base Models
The system SHALL provide a declarative base class for defining ORM models.

#### Scenario: Base class definition
- **WHEN** creating new database models
- **THEN** developers SHALL inherit from the `Base` class in `src/models/base.py`
- **AND** the base class SHALL use SQLAlchemy 2.0's `DeclarativeBase`
- **AND** models SHALL use `Mapped` type annotations for columns

#### Scenario: Common mixins
- **WHEN** models require common fields (timestamps, IDs)
- **THEN** the system SHALL provide reusable mixin classes
- **AND** timestamp mixins SHALL include `created_at` and `updated_at` fields
- **AND** mixins SHALL use SQLAlchemy's `mapped_column` with appropriate defaults

### Requirement: FastAPI Lifecycle Integration
The system SHALL integrate database lifecycle with FastAPI application events.

#### Scenario: Startup event
- **WHEN** the FastAPI application starts
- **THEN** it SHALL call `init_db()` to initialize the database schema
- **AND** it SHALL log successful database initialization
- **AND** startup SHALL fail if database initialization fails

#### Scenario: Shutdown event
- **WHEN** the FastAPI application shuts down
- **THEN** it SHALL dispose of the database engine
- **AND** it SHALL log the shutdown event
- **AND** all connections SHALL be closed before process termination

