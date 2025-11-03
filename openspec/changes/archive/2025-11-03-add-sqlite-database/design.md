# Database Layer Design

## Context
The Feishu bot application needs persistent storage for future features like conversation history, user sessions, and webhook event logging. SQLite provides a zero-configuration, file-based database suitable for development and small-to-medium production deployments. The application already has `sqlalchemy>=2.0.44` and `aiosqlite>=0.21.0` in dependencies.

**Constraints:**
- Must support async/await patterns (FastAPI standard)
- Should be simple to migrate to PostgreSQL/MySQL in the future
- Must work in development without external database setup
- Python 3.14+ compatibility required

**Stakeholders:**
- Developers building features requiring persistence
- Operations teams deploying the bot

## Goals / Non-Goals

**Goals:**
- Provide async database session management for FastAPI routes
- Initialize database schema on application startup
- Support future migration to other databases with minimal code changes
- Maintain clean separation between ORM models and Pydantic models

**Non-Goals:**
- Alembic migrations (defer to future change when schema stabilizes)
- Multi-database support (single database connection sufficient)
- Connection pooling optimization (SQLite default behavior acceptable)
- Read replicas or sharding (unnecessary complexity)

## Decisions

### Decision: Use SQLAlchemy 2.0 Async ORM
**Rationale:**
- Already in dependencies (`sqlalchemy>=2.0.44`)
- Industry standard with strong typing support
- Native async/await support in 2.0+
- Easy migration path to PostgreSQL/MySQL

**Alternatives considered:**
- Raw aiosqlite: Too low-level, requires manual SQL maintenance
- SQLModel: Adds dependency, less mature than SQLAlchemy 2.0

### Decision: Use Declarative Base with Mapped Annotations
**Rationale:**
- SQLAlchemy 2.0's modern API with type hints
- Better IDE support and type checking
- Clearer relationship to Python types

**Example:**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

### Decision: Database URL Configuration
Use environment variable `DATABASE_URL` with default:
- Development: `sqlite+aiosqlite:///./feishu-bot.sqlite` (relative path)
- Can override for testing: `sqlite+aiosqlite:///:memory:`
- Future production: `postgresql+asyncpg://...` (requires new driver)

### Decision: Schema Initialization Strategy
Use `Base.metadata.create_all()` on startup for simplicity:
- Automatically creates tables if they don't exist
- Idempotent (safe to run multiple times)
- No migration files needed until schema stabilizes
- When migrations are needed, can add Alembic in future change

### Decision: Session Management Pattern
Use FastAPI dependency injection with `async_sessionmaker`:
```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

@app.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db_session)):
    # Use db session
```

## Risks / Trade-offs

**Risk: SQLite concurrency limitations**
- Mitigation: Acceptable for bot workload (low write concurrency)
- Mitigation: Easy migration path to PostgreSQL if needed

**Risk: No migrations = manual schema updates**
- Mitigation: Document migration path for future (add Alembic later)
- Mitigation: Suitable for early-stage application

**Trade-off: Create tables on startup vs migrations**
- Pro: Simpler initial setup, no migration files to maintain
- Con: No version history, manual intervention for schema changes
- Decision: Accept trade-off for initial implementation

## Migration Plan

### Deployment Steps
1. Update code with database layer (non-breaking, database not used yet)
2. Set `DATABASE_URL` in environment (defaults to local SQLite)
3. Start application (tables auto-created on first run)
4. Verify database file exists and app starts successfully

### Rollback Plan
- Remove database lifecycle events from `app.py`
- Database file can be deleted (no data loss risk in initial implementation)

### Future Migration to PostgreSQL
When needed:
1. Install `asyncpg` driver: `uv add asyncpg`
2. Change `DATABASE_URL` to `postgresql+asyncpg://...`
3. SQLAlchemy code remains identical (ORM abstraction)
4. Consider adding Alembic for schema versioning

## Open Questions
None - design is straightforward and follows SQLAlchemy best practices.
