"""
Logging hook module for Amplifier.
Provides visibility into agent execution via lifecycle events.
"""

import logging
from pathlib import Path
from typing import Any

from amplifier_core import HookResult
from amplifier_core import ModuleCoordinator

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """
    Mount the logging hook.

    Args:
        coordinator: Module coordinator
        config: Hook configuration

    Returns:
        Optional cleanup function
    """
    # Immediate console output to verify module is loading
    print("🔍 [LOGGING MODULE] Mounting hooks-logging module...")
    config = config or {}
    hook = LoggingHook(config)
    await hook.register(coordinator)
    logger.info("Mounted LoggingHook")
    print("✓ [LOGGING MODULE] Logging hooks registered successfully")
    return


class LoggingHook:
    """Hook handlers for logging lifecycle events."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize logging hook.

        Args:
            config: Hook configuration with logging settings
        """
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Configure Python logging from config."""
        # Get logging configuration
        log_level = self.config.get("level", "INFO").upper()
        output = self.config.get("output", "console")
        log_file = self.config.get("file", "amplifier.log")

        print(f"🔍 [LOGGING MODULE] Configuring logging: level={log_level}, output={output}")

        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Add console handler
        if output in ("console", "both"):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # Add file handler
        if output in ("file", "both"):
            file_path = Path(log_file)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        logger.info(f"Logging configured: level={log_level}, output={output}")

    async def register(self, coordinator: ModuleCoordinator):
        """Register hook handlers with the coordinator."""
        hooks = coordinator.get("hooks")
        if not hooks:
            logger.warning("No hook registry found in coordinator")
            return

        # Register handlers for standard lifecycle events
        hooks.register("session:start", self.on_session_start, priority=0, name="logging:session_start")
        hooks.register("session:end", self.on_session_end, priority=0, name="logging:session_end")
        hooks.register("tool:pre", self.on_tool_pre, priority=0, name="logging:tool_pre")
        hooks.register("tool:post", self.on_tool_post, priority=0, name="logging:tool_post")
        hooks.register("agent:spawn", self.on_agent_spawn, priority=0, name="logging:agent_spawn")
        hooks.register("agent:complete", self.on_agent_complete, priority=0, name="logging:agent_complete")

        # Selection event handlers
        hooks.register("tool:selected", self.on_tool_selected, priority=0, name="logging:tool_selected")
        hooks.register("tool:selecting", self.on_tool_selecting, priority=0, name="logging:tool_selecting")

        # Error event handlers
        hooks.register("error:tool", self.on_tool_error, priority=0, name="logging:tool_error")
        hooks.register("error:provider", self.on_provider_error, priority=0, name="logging:provider_error")
        hooks.register(
            "error:orchestration", self.on_orchestration_error, priority=0, name="logging:orchestration_error"
        )

        logger.debug("Registered all logging hook handlers")

    # Hook event handlers

    async def on_session_start(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log session start."""
        prompt = data.get("prompt", "")
        logger.info("=== Session Started ===")
        logger.debug(f"Initial prompt: {prompt[:100]}...")
        return HookResult(action="continue")

    async def on_session_end(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log session end."""
        response = data.get("response", "")
        logger.info("=== Session Ended ===")
        logger.debug(f"Final response: {response[:100]}...")
        return HookResult(action="continue")

    async def on_tool_pre(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log tool invocation before execution."""
        tool_name = data.get("tool", "unknown")
        arguments = data.get("arguments", {})

        logger.info(f"Tool invoked: {tool_name}")
        logger.debug(f"Tool arguments: {arguments}")

        return HookResult(action="continue")

    async def on_tool_post(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log tool results after execution."""
        tool_name = data.get("tool", "unknown")
        result = data.get("result", {})

        # Extract success/error info
        if isinstance(result, dict):
            success = result.get("success", True)
            if success:
                logger.info(f"Tool completed: {tool_name} ✓")
                logger.debug(f"Tool result: {result}")
            else:
                error = result.get("error", "Unknown error")
                logger.warning(f"Tool failed: {tool_name} - {error}")
        else:
            logger.info(f"Tool completed: {tool_name}")
            logger.debug(f"Tool result: {result}")

        return HookResult(action="continue")

    async def on_agent_spawn(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log sub-agent spawning."""
        agent_type = data.get("agent_type", "unknown")
        task = data.get("task", "")

        logger.info(f"Sub-agent spawning: {agent_type}")
        logger.debug(f"Sub-agent task: {task[:100]}...")

        return HookResult(action="continue")

    async def on_agent_complete(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log sub-agent completion."""
        agent_type = data.get("agent_type", "unknown")

        logger.info(f"Sub-agent completed: {agent_type}")

        return HookResult(action="continue")

    # Selection event handlers

    async def on_tool_selecting(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log when tool selection is being considered."""
        tool = data.get("tool", "unknown")
        available = data.get("available_tools", [])

        logger.debug(f"Tool selection in progress: {tool} (available: {len(available)} tools)")

        return HookResult(action="continue")

    async def on_tool_selected(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log actual tool selection after decision is made."""
        tool = data.get("tool", "unknown")
        source = data.get("source", "unknown")
        original_tool = data.get("original_tool")

        if original_tool and original_tool != tool:
            logger.info(f"Tool selection: {tool} (overridden from {original_tool} by {source})")
        else:
            logger.info(f"Tool selection: {tool} (source: {source})")

        return HookResult(action="continue")

    # Error event handlers

    async def on_tool_error(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log tool errors with categorization."""
        error_type = data.get("error_type", "unknown")
        error_message = data.get("error_message", "")
        tool = data.get("tool", "unknown")
        severity = data.get("severity", "medium")
        stack_trace = data.get("stack_trace")

        # Log with appropriate level based on severity
        if severity == "critical":
            logger.critical(f"Tool error [{error_type}] in {tool}: {error_message}")
        elif severity == "high":
            logger.error(f"Tool error [{error_type}] in {tool}: {error_message}")
        elif severity == "medium":
            logger.warning(f"Tool error [{error_type}] in {tool}: {error_message}")
        else:
            logger.info(f"Tool error [{error_type}] in {tool}: {error_message}")

        if stack_trace:
            logger.debug(f"Stack trace: {stack_trace}")

        return HookResult(action="continue")

    async def on_provider_error(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log provider errors with categorization."""
        error_type = data.get("error_type", "unknown")
        error_message = data.get("error_message", "")
        severity = data.get("severity", "medium")

        # Log with appropriate level based on severity
        if severity in ("critical", "high"):
            logger.error(f"Provider error [{error_type}]: {error_message}")
        elif severity == "medium":
            logger.warning(f"Provider error [{error_type}]: {error_message}")
        else:
            logger.info(f"Provider error [{error_type}]: {error_message}")

        return HookResult(action="continue")

    async def on_orchestration_error(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log orchestration errors with categorization."""
        error_type = data.get("error_type", "unknown")
        error_message = data.get("error_message", "")
        severity = data.get("severity", "medium")

        # Log with appropriate level based on severity
        if severity in ("critical", "high"):
            logger.error(f"Orchestration error [{error_type}]: {error_message}")
        elif severity == "medium":
            logger.warning(f"Orchestration error [{error_type}]: {error_message}")
        else:
            logger.info(f"Orchestration error [{error_type}]: {error_message}")

        return HookResult(action="continue")
