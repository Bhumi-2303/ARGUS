"""Task dependency resolution using DAG."""
from typing import Dict, List, Set, Any
import structlog
from argus.core.exceptions import DependencyError

logger = structlog.get_logger("argus.orchestrator.dependency")

class DependencyResolver:
    """Resolves task dependencies using a Directed Acyclic Graph (DAG)."""
    
    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {} # task_id -> {dependency_ids}
        self._reverse_deps: Dict[str, Set[str]] = {} # dependency_id -> {task_ids}
        self._completed: Set[str] = set()
        
    def add_task(self, task_id: str, dependencies: List[str] = None) -> None:
        """Add a task and its dependencies to the graph."""
        deps = set(dependencies or [])
        self._dependencies[task_id] = deps
        
        for dep in deps:
            if dep not in self._reverse_deps:
                self._reverse_deps[dep] = set()
            self._reverse_deps[dep].add(task_id)
            
        # Detect cycles after adding
        self._detect_cycle()
        
    def resolve_order(self) -> List[str]:
        """Return a valid execution order for all tasks currently in the graph."""
        in_degree = {task: len(deps) for task, deps in self._dependencies.items()}
        queue = [task for task, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for dependent in self._reverse_deps.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
                    
        if len(result) != len(self._dependencies):
            raise DependencyError("Cycle detected or missing dependencies")
            
        return result
        
    def can_execute(self, task_id: str) -> bool:
        """Check if a task is ready to execute (all dependencies completed)."""
        if task_id not in self._dependencies:
            return True
        return all(dep in self._completed for dep in self._dependencies[task_id])
        
    def mark_complete(self, task_id: str) -> None:
        """Mark a task as complete, potentially freeing up dependent tasks."""
        self._completed.add(task_id)
        
    def _detect_cycle(self) -> None:
        """Detect cycles using DFS."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._dependencies.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False
            
        for node in list(self._dependencies.keys()):
            if node not in visited:
                if dfs(node):
                    raise DependencyError(f"Cycle detected involving task {node}")
