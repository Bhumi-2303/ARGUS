"""Priority task scheduler."""
import heapq
import time
from typing import Optional, Tuple
from argus.schemas.tasks import TaskDefinition

class PriorityScheduler:
    """Priority queue based task scheduler."""
    
    def __init__(self):
        # elements are (priority_value, timestamp, task_id, task_definition)
        self._queue = []
        self._task_map = {} # task_id -> task_definition
        
    def _get_priority_value(self, priority_str: str) -> int:
        priority_map = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        return priority_map.get(priority_str.lower(), 2)

    def enqueue(self, task_id: str, task: TaskDefinition) -> None:
        """Add a task to the queue."""
        priority_val = self._get_priority_value(task.priority)
        timestamp = time.time()
        
        heapq.heappush(self._queue, (priority_val, timestamp, task_id, task))
        self._task_map[task_id] = task

    def dequeue(self) -> Optional[Tuple[str, TaskDefinition]]:
        """Remove and return the highest priority task."""
        if not self._queue:
            return None
            
        _, _, task_id, task = heapq.heappop(self._queue)
        del self._task_map[task_id]
        return task_id, task
        
    def peek(self) -> Optional[Tuple[str, TaskDefinition]]:
        """Look at the highest priority task without removing it."""
        if not self._queue:
            return None
        _, _, task_id, task = self._queue[0]
        return task_id, task
        
    def size(self) -> int:
        """Return the number of queued tasks."""
        return len(self._queue)
        
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
        
    def remove(self, task_id: str) -> bool:
        """Remove a specific task by ID (O(N) operation)."""
        if task_id not in self._task_map:
            return False
            
        self._queue = [item for item in self._queue if item[2] != task_id]
        heapq.heapify(self._queue)
        del self._task_map[task_id]
        return True
