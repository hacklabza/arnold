# Copilot Instructions for Arnold

This document guides AI coding agents to be productive in the Arnold codebase. Follow these project-specific conventions and workflows for best results.

## Architecture Overview
- **Modular Design:** Arnold is a Raspberry Pi-based robotics platform. Code is organized by hardware function:
  - `motion/` (motor control)
  - `sensors/` (input devices)
  - `output/` (output devices)
  - `lookup/` (external API integrations)
  - `cli/` (command-line interface)
- **Configuration:** All hardware and integration settings are centralized in `arnold/config.py`. Update this file for pin assignments, API keys, and device parameters.
- **Main Entry:** The main logic is in `arnold/main.py`. Each module exposes a main class (e.g., `Speaker`, `DriveTrain`, `OpenAI`).

## Developer Workflows
- **Setup:**
  - Use `make install` to install system dependencies (see `README.md`).
  - Use `make poetry` to install Python dependencies via Poetry.
- **Testing:**
  - Run all tests with `make test`.
  - Module-specific tests are in `arnold/<module>/tests/`.
  - Some modules support CLI testing (e.g., `arnold test speaker --phrase "Hello World!"`).
- **Configuration:**
  - Hardware and API settings are in `arnold/config.py`. Example:
    ```python
    MOTION = { ... }
    SENSOR = { ... }
    OUTPUT = { ... }
    INTEGRATION = { ... }
    ```
- **Device Usage:**
  - Instantiate main classes from each module for hardware control. Example:
    ```python
    from arnold.motion import drivetrain
    drive = drivetrain.DriveTrain()
    drive.go('forward', 2)
    ```
  - For API lookups:
    ```python
    from arnold.lookup import openai
    openai = openai.OpenAI()
    response = openai.prompt(message="Hi!")
    ```

## Patterns & Conventions
- **Class-per-device:** Each hardware or integration module has a main class (e.g., `Speaker`, `Microphone`, `DriveTrain`).
- **Config-driven:** All device and API settings are loaded from `config.py`.
- **Testing:** Prefer CLI and Python unit tests in module-specific `tests/` folders.
- **Extensibility:** Add new hardware by creating a new module and updating `config.py`.

## Integration Points
- **External APIs:**
  - OpenAI integration via `lookup/openai.py` (API keys in config or env vars).
- **Hardware:**
  - GPIO pin assignments and device parameters in `config.py`.

## Key Files & Directories
- `arnold/config.py`: Central config for all modules
- `arnold/main.py`: Main entry point
- `arnold/<module>/`: Hardware/API modules
- `arnold/<module>/tests/`: Unit tests per module
- `README.md`: Setup, build, and usage instructions

---

If any section is unclear or missing, please provide feedback for improvement.
