"""
Workflow base class
"""
from abc import ABC, abstractmethod
import gradio as gr


class BaseWorkflow(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def icon(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    def build_tab(self):
        ...
