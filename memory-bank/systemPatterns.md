# System Patterns

## Architecture Overview

The Email Agent system employs a client-server architecture with these key components:

1. **Frontend (Next.js/React)**
   - Modern React application built with Next.js framework
   - Client-side components for real-time interactions
   - Server components for data fetching and rendering
   - TailwindCSS for styling

2. **Backend (Python/FastAPI)**
   - FastAPI application providing RESTful endpoints
   - SQLAlchemy ORM for database interactions
   - Pydantic models for data validation
   - Authentication middleware to secure endpoints

3. **Database (PostgreSQL)**
   - Stores all email metadata, user profiles, and categorization rules
   - Primary email storage remains with the email provider (Gmail)

## Key Design Patterns

### Category System

The categorization system is based on a weighted rule-based approach:

1. **Categories**
   - System categories: predefined categories like "Important", "Newsletters", "Social", etc.
   - User categories: custom categories created by users
   - Each category has a priority level for display ordering

2. **Classification Rules**
   - Keyword rules: Match words in subject or body
   - Sender rules: Match sender email domains or patterns
   - Weighted rules: Rules have configurable weights to influence categorization
   - ML-assisted classification: Uses training data for smarter categorization

3. **Rule Processing**
   - Multiple categorizers run in sequence
   - Weighted scoring determines final category
   - User overrides take precedence over system rules

### Component Design

1. **UI Components**
   - Modular design with specialized components
   - Reusable UI elements like forms, lists, and management interfaces
   - Context providers for shared state (categories, user settings)

2. **API Layer**
   - RESTful endpoints organized by resource
   - Clean separation of database models and API schemas
   - Middleware for authentication and error handling

3. **Email Processing**
   - Background processing for email synchronization
   - Reprocessing system for updating categories when rules change
   - Incremental processing to handle large mailboxes efficiently 