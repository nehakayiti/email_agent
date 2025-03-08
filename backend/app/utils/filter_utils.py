from typing import Dict, Any
from sqlalchemy.orm import Query

def apply_email_filters(query: Query, filter_params: Dict[str, Any]) -> Query:
    """
    Apply filters to an email query based on the provided parameters
    
    Args:
        query: Base SQLAlchemy query for Email objects
        filter_params: Dictionary of filter parameters
        
    Returns:
        Updated SQLAlchemy query with filters applied
    """
    if not filter_params:
        return query
        
    # Apply category filters
    if 'categories' in filter_params and filter_params['categories']:
        categories = filter_params['categories']
        if isinstance(categories, str):
            categories = [categories]
        query = query.filter(query.column_descriptions[0]['type'].category.in_(categories))
    
    # Apply date range filters
    if 'date_from' in filter_params and filter_params['date_from']:
        query = query.filter(query.column_descriptions[0]['type'].received_at >= filter_params['date_from'])
        
    if 'date_to' in filter_params and filter_params['date_to']:
        query = query.filter(query.column_descriptions[0]['type'].received_at <= filter_params['date_to'])
    
    # Apply search term filter
    if 'search' in filter_params and filter_params['search']:
        search_term = f"%{filter_params['search']}%"
        query = query.filter(
            (query.column_descriptions[0]['type'].subject.ilike(search_term)) | 
            (query.column_descriptions[0]['type'].from_email.ilike(search_term)) |
            (query.column_descriptions[0]['type'].snippet.ilike(search_term))
        )
    
    return query 