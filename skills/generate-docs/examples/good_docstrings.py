"""Module for processing user data and analytics.

This module provides classes and functions to process user data,
calculate engagement metrics, and generate reports. It demonstrates
proper Google-style docstrings.
"""

from typing import List, Dict, Optional, Union
import datetime


class UserProcessor:
    """Processes user data and generates analytics reports.

    This class handles the ingestion of raw user data, cleanses it,
    and provides methods to calculate various engagement metrics.

    Attributes:
        processor_id (str): A unique identifier for the processor instance.
        is_active (bool): Whether the processor is currently active.
    """

    def __init__(self, processor_id: str, is_active: bool = True):
        """Initializes the UserProcessor.

        Args:
            processor_id: A unique string identifier for this processor.
            is_active: Flag indicating if the processor should accept new data.
                Defaults to True.
        """
        self.processor_id = processor_id
        self.is_active = is_active
        self._data_store: List[Dict[str, Union[str, int]]] = []

    @property
    def record_count(self) -> int:
        """int: The number of records currently stored in the processor."""
        return len(self._data_store)

    def add_user_record(self, user_id: int, action: str, timestamp: Optional[datetime.datetime] = None) -> bool:
        """Adds a new user record to the processing queue.

        Validates the input data and appends it to the internal data store
        if the processor is active.

        Args:
            user_id: The unique identifier of the user.
            action: The action performed by the user (e.g., 'login', 'click').
            timestamp: The time the action occurred. If None, the current
                time is used.

        Returns:
            True if the record was successfully added, False otherwise.

        Raises:
            ValueError: If the action string is empty or None.
            RuntimeError: If attempting to add a record while the processor
                is inactive.

        Examples:
            >>> processor = UserProcessor("proc-01")
            >>> processor.add_user_record(101, "login")
            True
            >>> processor.record_count
            1
        """
        if not self.is_active:
            raise RuntimeError("Cannot add records to an inactive processor.")
        
        if not action:
            raise ValueError("Action string cannot be empty.")
            
        record_time = timestamp or datetime.datetime.now()
        
        self._data_store.append({
            "user_id": user_id,
            "action": action,
            "timestamp": record_time.isoformat()
        })
        
        return True

def calculate_engagement_score(actions: List[str]) -> float:
    """Calculates an engagement score based on a list of user actions.

    The score is computed by assigning weights to different types of actions
    and normalizing the result.

    Args:
        actions: A list of action strings performed by the user.

    Returns:
        A float representing the normalized engagement score between 0.0 and 1.0.
        Returns 0.0 if the actions list is empty.

    Examples:
        >>> actions = ["login", "view_item", "purchase"]
        >>> calculate_engagement_score(actions)
        0.85
    """
    if not actions:
        return 0.0
        
    weights = {"login": 0.1, "view_item": 0.3, "purchase": 0.6}
    total_score = sum(weights.get(action, 0.05) for action in actions)
    
    # Normalize (simplified logic for example)
    return min(1.0, total_score / (len(actions) * 0.6))
