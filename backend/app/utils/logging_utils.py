"""Logging utilities for email categorization system."""
import logging
import json
import time
from typing import Any, Dict, Optional
from functools import wraps
from uuid import UUID

logger = logging.getLogger(__name__)

class EmailLogger:
    """Centralized logging utility for email categorization system."""
    
    def __init__(self, correlation_id: str, component: str, user_id: Optional[UUID] = None):
        self.correlation_id = correlation_id
        self.component = component
        self.user_id = str(user_id) if user_id else "global"
        self.start_time = time.time()
    
    def _format_log(self, 
                    action: str, 
                    status: str = "info", 
                    details: Optional[Dict] = None, 
                    metrics: Optional[Dict] = None,
                    error: Optional[Exception] = None) -> Dict[str, Any]:
        """Format log entry with standard structure."""
        log_entry = {
            "correlation_id": self.correlation_id,
            "component": self.component,
            "action": action,
            "status": status,
            "user_id": self.user_id,
            "timestamp": time.time()
        }
        
        if details:
            # Limit size of detail values
            sanitized_details = {}
            for k, v in details.items():
                if isinstance(v, str) and len(v) > 1000:
                    sanitized_details[k] = v[:1000] + "..."
                else:
                    sanitized_details[k] = v
            log_entry["details"] = sanitized_details
            
        if metrics:
            log_entry["metrics"] = metrics
            
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error)
            }
        
        return log_entry
    
    def debug(self, action: str, details: Optional[Dict] = None, metrics: Optional[Dict] = None):
        """Log debug level event."""
        if logger.isEnabledFor(logging.DEBUG):
            log_entry = self._format_log(action, "debug", details, metrics)
            logger.debug(self.component, extra=log_entry)
    
    def info(self, action: str, details: Optional[Dict] = None, metrics: Optional[Dict] = None):
        """Log info level event."""
        if logger.isEnabledFor(logging.INFO):
            log_entry = self._format_log(action, "info", details, metrics)
            logger.info(self.component, extra=log_entry)
    
    def warning(self, action: str, details: Optional[Dict] = None, metrics: Optional[Dict] = None):
        """Log warning level event."""
        log_entry = self._format_log(action, "warning", details, metrics)
        logger.warning(self.component, extra=log_entry)
    
    def error(self, action: str, error: Exception, details: Optional[Dict] = None):
        """Log error level event."""
        log_entry = self._format_log(action, "error", details, error=error)
        logger.error(self.component, extra=log_entry, exc_info=True)
    
    def start_operation(self, operation: str, details: Optional[Dict] = None):
        """Log start of an operation."""
        self.operation_start = time.time()
        self.current_operation = operation
        if logger.isEnabledFor(logging.DEBUG):
            self.debug(f"Starting {operation}", details)
    
    def end_operation(self, details: Optional[Dict] = None):
        """Log end of an operation with duration."""
        duration_ms = round((time.time() - self.operation_start) * 1000, 2)
        metrics = {"duration_ms": duration_ms}
        self.info(
            f"Completed {self.current_operation}",
            details=details,
            metrics=metrics
        )

def log_operation(name: str):
    """Decorator to log function execution time and status."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get email_logger from self if it's a method
            if args and hasattr(args[0], 'email_logger'):
                email_logger = args[0].email_logger
                # Create a default logger if email_logger is None
                if email_logger is None:
                    correlation_id = kwargs.get('email_id', 'unknown')
                    if hasattr(args[0], 'user_id'):
                        user_id = args[0].user_id
                    else:
                        user_id = None
                    email_logger = EmailLogger(correlation_id, "AUTO_CREATED", user_id)
                    # Assign it back to the instance to prevent future issues
                    args[0].email_logger = email_logger
            else:
                # Create temporary logger for standalone functions
                correlation_id = kwargs.get('email_id', 'unknown')
                email_logger = EmailLogger(correlation_id, "function")
            
            email_logger.start_operation(name)
            try:
                result = func(*args, **kwargs)
                email_logger.end_operation()
                return result
            except Exception as e:
                email_logger.error(f"Error in {name}", e)
                raise
        return wrapper
    return decorator

def summarize_matches(matches: list, max_items: int = 3) -> dict:
    """Summarize match data for logging."""
    if not matches:
        return {"count": 0}
    
    return {
        "count": len(matches),
        "top_matches": matches[:max_items],
        "has_more": len(matches) > max_items
    }

def sanitize_email(email: str) -> str:
    """Sanitize email address for logging."""
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        return email
    return f"{local[:2]}...@{domain}" 