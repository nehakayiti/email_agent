# Technical Context

## Technology Stack

### Frontend
- **Framework**: Next.js 15.x with React 19.x
- **Styling**: TailwindCSS with custom components
- **State Management**: React Context API
- **UI Libraries**:
  - HeroIcons for icons
  - React Hot Toast for notifications
  - Chart.js for analytics visualizations
- **Data Fetching**: Custom fetch wrapper with auth handling

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **Authentication**: JWT tokens
- **Email Integration**: Gmail API
- **Machine Learning**: scikit-learn for classification models

### Database
- **Primary Database**: PostgreSQL
- **Schema**: Relational with specialized tables for emails, categories, and classification rules

## Development Environment

- **Package Management**: 
  - npm/yarn for frontend
  - pip/virtualenv for backend
- **Testing**: 
  - Playwright for end-to-end testing
  - pytest for backend testing
- **Code Quality**: 
  - ESLint and TypeScript for frontend
  - mypy and Black for Python
  
## API Structure

The backend API is organized into these main areas:

1. **Authentication APIs**
   - Login, logout, token refresh
   - OAuth2 flow for Gmail integration

2. **Email Management APIs**
   - Email fetching and syncing
   - Email categorization and labeling
   - Search and filtering

3. **Category Management APIs**
   - CRUD operations for categories
   - Rule management endpoints (keywords, sender rules)
   - Category initialization endpoints

4. **Analytics APIs**
   - Email statistics
   - Category distribution
   - Classification metrics

## Key Models

### Email Categories
```python
class EmailCategory(Base):
    __tablename__ = "email_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, default=50)
    is_system = Column(Boolean, default=False)
    created_at = Column(JSONB, nullable=True)
    
    # Relationships
    keywords = relationship("CategoryKeyword", back_populates="category")
    sender_rules = relationship("SenderRule", back_populates="category")
```

### Classification Rules
```python
class CategoryKeyword(Base):
    __tablename__ = "category_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("email_categories.id"))
    keyword = Column(String, nullable=False)
    is_regex = Column(Boolean, default=False)
    weight = Column(Integer, default=1)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    category = relationship("EmailCategory", back_populates="keywords")

class SenderRule(Base):
    __tablename__ = "sender_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("email_categories.id"))
    pattern = Column(String, nullable=False)
    is_domain = Column(Boolean, default=True)
    weight = Column(Integer, default=1)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    category = relationship("EmailCategory", back_populates="sender_rules")
``` 