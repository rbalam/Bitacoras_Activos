from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

# Configuration Models
class ConfigBase(BaseModel):
    key: str
    value: str
    category: Literal["twilio", "email", "sql_server", "general"]
    description: Optional[str] = None
    is_sensitive: bool = True
    active: bool = True

class ConfigCreate(ConfigBase):
    pass

class ConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

class Config(ConfigBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None

class ConfigPublic(BaseModel):
    """Public view of config (hides sensitive values)"""
    id: str
    key: str
    value: str  # Will show masked value for sensitive configs
    category: str
    description: Optional[str] = None
    is_sensitive: bool
    active: bool
    updated_at: datetime


class TestNotificationRequest(BaseModel):
    test_email: EmailStr
    test_phone: Optional[str] = None
