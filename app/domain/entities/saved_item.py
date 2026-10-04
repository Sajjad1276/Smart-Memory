from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SavedItem:
    id: UUID
    user_id: UUID
    storage_message_id: int
    content_type: str
    source_type: str
    saved_at: datetime
