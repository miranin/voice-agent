from pydantic import BaseModel, Field
from typing import Optional


class Event(BaseModel):
    title: str
    date: Optional[str] = None        # "2026-03-12"
    time: Optional[str] = None        # "19:00"
    location: Optional[str] = None
    price: Optional[str] = None
    url: Optional[str] = None
    source: str                        # "sxodim" | "ticketon" | "kino"
    category: Optional[str] = None    # "concert" | "standup" | "movie" | "exhibition"

    def to_agent_text(self) -> str:
        """Human-readable string for LLM context."""
        parts = [f"• {self.title}"]
        if self.date:
            parts.append(f"  Date: {self.date}")
        if self.time:
            parts.append(f"  Time: {self.time}")
        if self.location:
            parts.append(f"  Location: {self.location}")
        if self.price:
            parts.append(f"  Price: {self.price}")
        if self.url:
            parts.append(f"  Link: {self.url}")
        return "\n".join(parts)
