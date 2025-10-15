# Amplifier Logging Hook Module

Provides visibility into agent execution through lifecycle event logging.

## Overview

This hook module integrates with Amplifier's hook system to log all standard lifecycle events:

- Session start/end
- Tool invocations and results
- Sub-agent spawning and completion
- Errors and warnings

## Features

- **Zero code changes required** - pure configuration
- **Standard Python logging** - no external dependencies
- **Configurable levels** - DEBUG, INFO, WARNING, ERROR
- **Flexible output** - console, file, or both
- **Clean formatting** - timestamp, level, module, message

## Prerequisites

- **Python 3.11+**
- **[UV](https://github.com/astral-sh/uv)** - Fast Python package manager

### Installing UV

```bash
# macOS/Linux/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

```bash
uv pip install -e ./amplifier-module-hooks-logging
```

## Configuration

Add to your Amplifier configuration file (e.g., `test-full-features.toml`):

```toml
[hooks]
enabled = ["logging"]

[hooks.logging]
level = "INFO"           # DEBUG, INFO, WARNING, ERROR, CRITICAL
output = "console"       # console, file, or both
file = "amplifier.log"   # Required if output includes "file"
```

## Log Levels

### INFO (Recommended)

Shows key events without overwhelming detail:

- Session lifecycle
- Tool invocations (name only)
- Sub-agent activity
- Errors and warnings

### DEBUG

Shows all details:

- Tool arguments and results
- Full message content
- Provider interactions
- All lifecycle events

### WARNING

Shows only warnings and errors:

- Tool failures
- Performance issues
- Configuration problems

### ERROR

Shows only errors:

- Critical failures
- Unhandled exceptions

## Usage

Once configured, logging happens automatically. No code changes needed.

```bash
# Start Amplifier with logging enabled
amplifier run --config test-full-features.toml --mode chat
```

## Example Output

```
2025-10-06 12:00:00 [INFO] amplifier_module_hooks_logging: === Session Started ===
2025-10-06 12:00:01 [INFO] amplifier_module_hooks_logging: Tool invoked: grep
2025-10-06 12:00:02 [INFO] amplifier_module_hooks_logging: Tool completed: grep ✓
2025-10-06 12:00:05 [INFO] amplifier_module_hooks_logging: Sub-agent spawning: architect
2025-10-06 12:00:10 [INFO] amplifier_module_hooks_logging: Sub-agent completed: architect
2025-10-06 12:00:11 [INFO] amplifier_module_hooks_logging: === Session Ended ===
```

## Philosophy Alignment

This module follows Amplifier's core principles:

- **Ruthless Simplicity**: Uses standard Python logging, no complexity
- **Modular Design**: Self-contained, enable/disable via config
- **Zero Abstraction**: Direct logging calls, no wrappers
- **Separation of Concerns**: Logging logic separate from business logic

## Development

### Adding Dependencies

```bash
# Add runtime dependency
uv add pydantic

# Add development dependency
uv add --dev pytest

# Update dependencies
uv lock --upgrade
```

### Running Tests

```bash
uv run pytest
```

### Running Tests

```bash
uv run pytest tests/
```

### Adding New Event Handlers

To log additional events, register a handler in the `LoggingHook.register()` method:

```python
hooks.register("custom:event", self.on_custom_event, priority=0, name="logging:custom")
```

Then implement the handler:

```python
async def on_custom_event(self, event: str, data: dict[str, Any]) -> HookResult:
    """Log custom event."""
    logger.info(f"Custom event occurred: {data}")
    return HookResult(action="continue")
```

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
