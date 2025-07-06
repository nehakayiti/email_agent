from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Valid action types for email processing"""
    ARCHIVE = "ARCHIVE"
    TRASH = "TRASH"

class ActionRuleRequest(BaseModel):
    """Request model for creating or updating action rules"""
    model_config = ConfigDict(from_attributes=True)
    
    action: ActionType = Field(..., description="Type of action to perform")
    delay_days: int = Field(..., ge=0, le=365, description="Days to wait before applying action")
    enabled: bool = Field(True, description="Whether the action rule is enabled")
    
    @field_validator('delay_days')
    @classmethod
    def validate_delay_days(cls, v):
        if v < 0:
            raise ValueError('Delay days must be non-negative')
        if v > 365:
            raise ValueError('Delay days cannot exceed 365')
        return v

class ActionRuleResponse(BaseModel):
    """Response model for action rule information"""
    model_config = ConfigDict(from_attributes=True)
    
    category_id: int = Field(..., description="ID of the category")
    category_name: str = Field(..., description="Name of the category")
    action: Optional[ActionType] = Field(None, description="Type of action configured")
    delay_days: Optional[int] = Field(None, description="Days to wait before applying action")
    enabled: bool = Field(False, description="Whether the action rule is enabled")

class ActionPreviewResponse(BaseModel):
    """Response model for action preview information"""
    category_id: int = Field(..., description="ID of the category")
    affected_email_count: int = Field(..., description="Number of emails that would be affected")
    affected_emails: List[Dict[str, Any]] = Field(..., description="Preview of affected emails")

class ProposedActionStatus(str, Enum):
    """Status of proposed actions"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ProposedActionItem(BaseModel):
    """Individual proposed action item"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique identifier for the proposed action")
    email_id: str = Field(..., description="ID of the email being acted upon")
    email_subject: str = Field(..., description="Subject of the email")
    email_sender: str = Field(..., description="Sender of the email")
    email_date: Optional[datetime] = Field(None, description="Date the email was received")
    category_id: int = Field(..., description="ID of the category that triggered the action")
    category_name: str = Field(..., description="Name of the category")
    action_type: ActionType = Field(..., description="Type of action proposed")
    reason: str = Field(..., description="Explanation of why the action is proposed")
    email_age_days: int = Field(..., description="Age of the email in days")
    created_at: datetime = Field(..., description="When the proposal was created")
    status: ProposedActionStatus = Field(..., description="Current status of the proposal")

class ProposedActionList(BaseModel):
    """Paginated list of proposed actions"""
    items: List[ProposedActionItem] = Field(..., description="List of proposed actions")
    total_count: int = Field(..., description="Total number of proposed actions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

class BulkActionRequest(BaseModel):
    """Request model for bulk operations on proposed actions"""
    model_config = ConfigDict(from_attributes=True)
    
    action_ids: List[str] = Field(..., min_length=1, max_length=100, description="List of action IDs to process")
    
    @field_validator('action_ids')
    @classmethod
    def validate_action_ids(cls, v):
        if not v:
            raise ValueError('At least one action ID must be provided')
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 actions at once')
        return v

class ActionProcessRequest(BaseModel):
    """Request model for processing actions (dry run or execute)"""
    model_config = ConfigDict(from_attributes=True)
    
    category_ids: Optional[List[int]] = Field(None, description="Specific categories to process (None = all)")
    force: bool = Field(False, description="Force processing even if no changes detected")
    
    @field_validator('category_ids')
    @classmethod
    def validate_category_ids(cls, v):
        if v is not None and len(v) > 50:
            raise ValueError('Cannot process more than 50 categories at once')
        return v

class ActionProcessResponse(BaseModel):
    """Response model for action processing results"""
    success: bool = Field(..., description="Whether the processing was successful")
    mode: str = Field(..., description="Processing mode (dry_run or execute)")
    proposals_created: Optional[int] = Field(None, description="Number of proposals created (dry run mode)")
    operations_created: Optional[int] = Field(None, description="Number of operations created (execute mode)")
    emails_processed: int = Field(..., description="Number of emails processed")
    message: str = Field(..., description="Human-readable result message")
    errors: Optional[List[str]] = Field(None, description="List of errors encountered during processing")

class ActionStatsResponse(BaseModel):
    """Response model for action statistics"""
    total_proposals: int = Field(..., description="Total number of proposed actions")
    by_status: Dict[str, int] = Field(..., description="Counts by status")
    by_action_type: Dict[str, int] = Field(..., description="Counts by action type")
    recent_activity: Optional[List[Dict[str, Any]]] = Field(None, description="Recent activity summary")

class ActionRuleValidationResponse(BaseModel):
    """Response model for action rule validation"""
    valid: bool = Field(..., description="Whether the action rule is valid")
    error: Optional[str] = Field(None, description="Error message if validation failed")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")

class BulkActionResponse(BaseModel):
    """Response model for bulk action operations"""
    message: str = Field(..., description="Result message")
    processed_count: int = Field(..., description="Number of actions successfully processed")
    failed_count: int = Field(..., description="Number of actions that failed")
    failed_actions: List[Dict[str, str]] = Field(..., description="Details of failed actions")

class CleanupResponse(BaseModel):
    """Response model for cleanup operations"""
    message: str = Field(..., description="Result message")
    expired_proposals_removed: int = Field(..., description="Number of expired proposals removed") 