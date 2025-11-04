# Database Schema - Available Now Bot

## Overview

This document describes the database schema for the Available Now bot. The current implementation uses in-memory storage, but this schema is designed for future SQLAlchemy + PostgreSQL integration.

## Tables

### 1. users
Stores information about bot users (models/admins).

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,  -- Telegram user ID
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_approved_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. profiles
Stores model profiles.

```sql
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    about TEXT,
    contact_method VARCHAR(50),  -- 'phone', 'email', 'telegram'
    phone VARCHAR(20),
    email VARCHAR(255),
    telegram_username VARCHAR(255),
    social_links TEXT,  -- JSON or plain text
    rates TEXT,
    disclaimer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 3. offer_types
Stores the services offered by each model.

```sql
CREATE TABLE offer_types (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL,
    service_type VARCHAR(50),  -- 'in_person', 'facetime', 'custom', 'other'
    in_person_type VARCHAR(50),  -- 'Incall Only', 'Outcall Only', 'Incall/Outcall'
    in_person_location VARCHAR(255),
    facetime_platforms VARCHAR(255),
    facetime_payment VARCHAR(255),
    custom_payment VARCHAR(255),
    custom_delivery VARCHAR(255),
    other_service TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
```

### 4. media
Stores images and videos associated with profiles.

```sql
CREATE TABLE media (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL,
    file_id VARCHAR(255) NOT NULL,  -- Telegram file ID
    media_type VARCHAR(50),  -- 'image' or 'video'
    position INTEGER,  -- Order in gallery
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
```

### 5. listings
Stores active availability listings.

```sql
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    profile_id INTEGER NOT NULL,
    message_id BIGINT NOT NULL UNIQUE,  -- Telegram message ID
    group_id BIGINT NOT NULL,  -- Telegram group ID
    duration_hours INTEGER,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,  -- NULL if still active
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
```

### 6. audit_log
Stores audit trail for security and debugging.

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(255),  -- 'create_profile', 'mark_available', 'delete_listing', etc.
    details TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes

```sql
-- Performance optimization
CREATE INDEX idx_users_telegram_id ON users(id);
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_offer_types_profile_id ON offer_types(profile_id);
CREATE INDEX idx_media_profile_id ON media(profile_id);
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_expires_at ON listings(expires_at);
CREATE INDEX idx_listings_message_id ON listings(message_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

## Relationships

```
users (1) ──────────── (N) profiles
users (1) ──────────── (N) listings
profiles (1) ────────── (N) offer_types
profiles (1) ────────── (N) media
profiles (1) ────────── (N) listings
```

## Data Types

- **BIGINT**: For Telegram IDs (can be very large)
- **SERIAL**: For auto-incrementing primary keys
- **VARCHAR(255)**: For strings with maximum length
- **TEXT**: For longer text content
- **TIMESTAMP**: For date/time tracking
- **BOOLEAN**: For true/false flags

## Migration Path

To migrate from in-memory storage to database:

1. Install SQLAlchemy:
   ```bash
   pip install sqlalchemy psycopg2-binary alembic
   ```

2. Create models.py with SQLAlchemy models matching this schema

3. Create database migrations using Alembic

4. Update bot.py to use SQLAlchemy instead of ProfileDatabase class

5. Test thoroughly before deploying to production

## Example SQLAlchemy Models

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_approved_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profiles = relationship('Profile', back_populates='user')
    listings = relationship('Listing', back_populates='user')

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    name = Column(String(255), nullable=False)
    about = Column(Text)
    contact_method = Column(String(50))
    phone = Column(String(20))
    email = Column(String(255))
    telegram_username = Column(String(255))
    social_links = Column(Text)
    rates = Column(Text)
    disclaimer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='profiles')
    offer_types = relationship('OfferType', back_populates='profile')
    media = relationship('Media', back_populates='profile')
    listings = relationship('Listing', back_populates='profile')

# ... additional models follow similar pattern
```

## Performance Considerations

1. **Indexing**: All foreign keys and frequently queried fields are indexed
2. **Partitioning**: Consider partitioning `listings` and `audit_log` by date for large-scale deployments
3. **Archiving**: Archive old listings and audit logs to separate tables
4. **Caching**: Use Redis for frequently accessed profiles
5. **Connection Pooling**: Use SQLAlchemy connection pooling for better performance

## Backup Strategy

1. Daily automated backups to S3
2. Point-in-time recovery enabled
3. Regular backup restoration tests
4. Encrypted backups at rest

## Security

1. All sensitive data encrypted at rest
2. SQL injection prevention through parameterized queries
3. Row-level security for multi-tenant scenarios
4. Audit logging for all modifications
5. Regular security audits and penetration testing
