"""
Workflow registry
"""
from workflows.base import BaseWorkflow


class WorkflowRegistry:

    def __init__(self):
        self._workflows: list[BaseWorkflow] = []

    def register(self, workflow: BaseWorkflow):
        self._workflows.append(workflow)
        return workflow

    def get_all(self) -> list[BaseWorkflow]:
        return list(self._workflows)


workflow_registry = WorkflowRegistry()
