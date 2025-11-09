"""
Base Agent class - Foundation for all agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents"""

    def __init__(self, name: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.3):
        """
        Initialize base agent

        Args:
            name: Agent name
            model: Groq model to use
            temperature: LLM temperature (0.0-1.0)
        """
        self.name = name
        self.model = model
        self.temperature = temperature
        self.llm = self._initialize_llm()
        self.memory = []  # Agent memory for context

    def _initialize_llm(self) -> ChatGroq:
        """Initialize Groq LLM"""
        try:
            return ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=self.model,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM for {self.name}: {e}")
            raise

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        pass

    def add_to_memory(self, item: str):
        """Add item to agent memory"""
        self.memory.append(item)
        # Keep only last 10 items
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]

    def get_context(self) -> str:
        """Get agent memory as context string"""
        return "\n".join(self.memory)

    def log(self, message: str, level: str = "info"):
        """Log agent activity"""
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{self.name}] {message}")

    async def invoke_llm(self, prompt: str) -> str:
        """
        Invoke LLM with prompt

        Args:
            prompt: Prompt text

        Returns:
            LLM response
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.log(f"LLM invocation failed: {e}", "error")
            raise

    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format prompt template with variables

        Args:
            template: Prompt template string
            **kwargs: Template variables

        Returns:
            Formatted prompt
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.log(f"Missing template variable: {e}", "error")
            raise

    async def retry_on_failure(self, func, max_retries: int = 3, *args, **kwargs):
        """
        Retry function on failure

        Args:
            func: Function to retry
            max_retries: Maximum retry attempts
            *args, **kwargs: Function arguments

        Returns:
            Function result
        """
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.log(f"Attempt {attempt + 1} failed: {e}", "warning")
                if attempt == max_retries - 1:
                    raise
                await self._wait_before_retry(attempt)

    async def _wait_before_retry(self, attempt: int):
        """Wait before retrying (exponential backoff)"""
        import asyncio
        wait_time = 2 ** attempt
        self.log(f"Waiting {wait_time}s before retry...")
        await asyncio.sleep(wait_time)


class AgentResponse:
    """Standardized agent response"""

    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None, metadata: Dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }
