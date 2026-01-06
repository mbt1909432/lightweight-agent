"""Conversation History Management"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Message:
    """Message model"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format (for API calls)"""
        result = {
            "role": self.role,
            "content": self.content,
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


class MessageHistory:
    """Message history management"""
    
    def __init__(
        self,
        max_messages: Optional[int] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize message history
        
        :param max_messages: Maximum number of messages (None=unlimited)
        :param max_tokens: Maximum token count (for truncation, None=unlimited)
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
    
    def add(
        self,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None
    ) -> None:
        """
        Add message
        
        :param role: Message role
        :param content: Message content
        :param tool_calls: Tool calls (only for assistant messages)
        :param tool_call_id: Tool call ID (only for tool messages)
        """
        message = Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id
        )
        self.messages.append(message)
        
        # If max messages is set, keep the most recent N messages (keep system messages)
        if self.max_messages and len(self.messages) > self.max_messages:
            system_messages = [m for m in self.messages if m.role == "system"]
            other_messages = [m for m in self.messages if m.role != "system"]
            # Keep system messages + most recent N other messages
            keep_count = self.max_messages - len(system_messages)
            if keep_count > 0:
                self.messages = system_messages + other_messages[-keep_count:]
            else:
                self.messages = system_messages
    
    def get_formatted(self) -> List[Dict[str, Any]]:
        """
        Get formatted message list (for API calls)
        
        :return: List of message dictionaries
        """
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self, keep_system: bool = True) -> None:
        """
        Clear message history
        
        :param keep_system: Whether to keep system messages
        """
        if keep_system:
            self.messages = [m for m in self.messages if m.role == "system"]
        else:
            self.messages = []
    
    def __len__(self) -> int:
        """Return number of messages"""
        return len(self.messages)
    
    def __iter__(self):
        """Iterate messages"""
        return iter(self.messages)

