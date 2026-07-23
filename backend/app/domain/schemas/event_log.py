from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventLogResponse(BaseModel):
    event_id: str
    event_type: str
    payload: dict
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
