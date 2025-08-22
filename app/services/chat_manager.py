import collections
from collections import defaultdict
from typing import List, Dict, Deque

# We store 10 items to keep 5 pairs of user/assistant messages
MAX_HISTORY_LENGTH = 10 

class ChatManager:
    """
    Manages conversation histories for multiple sessions.
    """
    def __init__(self):
        """
        Initializes the history store.
        """
        self.histories: Dict[str, Deque] = defaultdict(
            lambda: collections.deque(maxlen=MAX_HISTORY_LENGTH)
        )

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieves the conversation history for a given session.
        """
        return list(self.histories[session_id])

    def add_to_history(self, session_id: str, user_message: str, ai_message: str):
        """
        Adds a user message and an AI response to the session's history.
        """
        self.histories[session_id].append({"role": "user", "content": user_message})
        self.histories[session_id].append({"role": "assistant", "content": ai_message})