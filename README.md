# Appium Python Automation Framework

A robust and scalable mobile automation testing framework built with Python, Appium, and pytest for Android application testing.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Logging](#logging)
- [Reporting](#reporting)
- [Screenshots](#screenshots)
- [Best Practices](#best-practices)

---

## Overview

This framework is designed for automating Android mobile applications using Appium with Python. It follows the Page Object Model (POM) design pattern, making tests maintainable, scalable, and easy to understand. The framework automatically handles Appium server lifecycle, captures screenshots on test completion, and generates HTML reports.

**Target Application:** General Store (com.androidsample.generalstore)

---

## Project Structure

```
appium-python-framework/
├── config/
│   └── desired_caps.py       # Device capabilities configuration
├── logs/
│   ├── pytest.log            # Pytest execution logs
│   └── tool.log              # Custom tool logs
├── pages/
│   ├── base_page.py          # Base page class with common functionality
│   └── home_page.py          # Home page object with element locators & actions
├── reports/
│   └── report.html           # HTML test report (auto-generated)
├── screenshots/
│   └── *.png                 # Test screenshots (auto-generated)
├── tests/
│   ├── test_home.py          # Test cases for home page
│   └── test_home2.py         # Additional test cases
├── utilities/
│   ├── driver_factory.py     # WebDriver initialization
│   ├── log_handler.py        # Custom logging configuration
│   └── utils.py              # Utility functions (Appium server management)
├── appium.log                # Appium server logs
├── conftest.py               # Pytest fixtures and hooks
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Features

- **Page Object Model (POM):** Clean separation between test logic and page interactions
- **Automatic Appium Server Management:** Starts/stops Appium server automatically
- **Screenshot Capture:** Captures screenshots after each test (pass or fail)
- **HTML Reports:** Generates detailed HTML reports with embedded screenshots
- **Comprehensive Logging:** Dual logging system (console + file)
- **Implicit & Explicit Waits:** Built-in wait handling for stable test execution
- **Cross-Platform Support:** Compatible with Windows OS

---

## Prerequisites

Before running the tests, ensure you have the following installed:

### Software Requirements

| Software | Purpose |
|----------|---------|
| Python 3.8+ | Programming language runtime |
| Node.js | Required for Appium |
| Appium 2.x | Mobile automation framework |
| Appium Doctor | For verifying Appium setup |
| Android Studio | Android SDK and emulator |
| Java JDK 8+ | Required by Android SDK |

### Environment Setup

1. **Install Appium globally:**
   ```bash
   npm install -g appium
   ```

2. **Install UiAutomator2 driver:**
   ```bash
   appium driver install uiautomator2
   ```

3. **Set ANDROID_HOME environment variable:**
   ```bash
   # Windows
   setx ANDROID_HOME "C:\Users\<username>\AppData\Local\Android\Sdk"
   
   # Add to PATH
   setx PATH "%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools"
   ```

4. **Connect Android device or start emulator:**
   - Enable USB debugging on physical device
   - Or create and start an Android Virtual Device (AVD)

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd appium-python-framework
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies
| Package | Purpose |
|---------|---------|
| Appium-Python-Client | Appium Python client library |
| pytest | Testing framework |
| pytest-html | HTML report generation |
| selenium | WebDriver support |
| psutil | Process management for server control |

---

## Configuration

### Device Capabilities (`config/desired_caps.py`)

Configure your target device and application:

```python
caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android Device",
    "appPackage": "com.androidsample.generalstore",
    "appActivity": "com.androidsample.generalstore.SplashActivity"
}
```

| Capability | Description |
|------------|-------------|
| `platformName` | Mobile platform (Android/iOS) |
| `automationName` | Automation engine (UiAutomator2 for Android) |
| `deviceName` | Device identifier |
| `appPackage` | Application package name |
| `appActivity` | Main activity to launch |

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
addopts = -v -s --html=reports/report.html --self-contained-html
log_cli = true
log_cli_level = INFO
log_file = logs/pytest.log
log_file_level = INFO
```

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_home.py
```

### Run Specific Test Method
```bash
pytest tests/test_home.py::TestHome::test_user_registration
```

### Run with Verbose Output
```bash
pytest -v -s
```

### Run Tests in Parallel (requires pytest-xdist)
```bash
pip install pytest-xdist
pytest -n 2
```

---

## Architecture

### Test Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST SESSION START                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  conftest.py: appium_server fixture (session-scoped)         │
│  - Starts Appium server on port 4725                         │
│  - Stops existing server if port is occupied                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  conftest.py: driver fixture (function-scoped)               │
│  - Creates WebDriver instance                                │
│  - Yields driver to test                                    │
│  - Captures screenshot after test                           │
│  - Quits driver                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TEST EXECUTION                            │
│  - Page Objects interact with elements                       │
│  - Actions are logged via log_handler                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              HTML REPORT GENERATION                          │
│  - pytest-html generates report                              │
│  - Screenshots embedded in report                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TEST SESSION END                          │
│  - Appium server stopped                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. conftest.py - Pytest Configuration

**Fixtures:**

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `appium_server` | Session | Starts/stops Appium server once per test run |
| `driver` | Function | Creates WebDriver instance for each test |

**Hooks:**
- `pytest_runtest_makereport`: Attaches screenshots to HTML reports
- `pytest_configure`: Registers pytest-html plugin

### 2. utilities/driver_factory.py

Creates and configures the Appium WebDriver instance:

```python
def get_driver():
    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4725",
        options=options
    )
    driver.implicitly_wait(10)
    return driver
```

### 3. utilities/utils.py

**Utils Class Methods:**

| Method | Purpose |
|--------|---------|
| `is_port_in_use(port)` | Checks if a port is occupied |
| `stop_existing_appium_server(port)` | Terminates existing server on port |
| `start_appium_server(port)` | Starts new Appium server |
| `stop_appium_server()` | Stops the running server |
| `setup_module(app_name)` | Alternative setup for module-level tests |
| `teardown_module()` | Cleanup for module-level tests |

### 4. utilities/log_handler.py

Custom logging system with:
- **Console Handler:** Colored output (red prefix)
- **File Handler:** Plain text logs to `logs/tool.log`

**Usage:**
```python
from utilities.log_handler import nowLogs
nowLogs("Message to log")
```

**Log Format:**
```
YYYY-MM-DD HH:MM:SS | LEVEL    | Appium | filename.py:lineno :message
```

### 5. pages/base_page.py

Base class for all page objects:
```python
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(10)
```

### 6. pages/home_page.py

Home page object with element locators and interaction methods:

| Method | Action |
|--------|--------|
| `select_country(country_name)` | Selects country from dropdown |
| `enter_name(name)` | Enters name in text field |
| `select_male()` | Selects male gender radio button |
| `click_shop()` | Clicks shop button |

**Locators:**
- `name_field`: Name input field
- `male_radio`: Male gender radio button
- `shop_button`: Shop button

---

## Logging

### Log Files

| File | Content |
|------|---------|
| `logs/tool.log` | Custom application logs |
| `logs/pytest.log` | Pytest execution logs |
| `appium.log` | Appium server logs |

### Log Levels

The framework supports multiple log levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General execution information
- `WARNING`: Potential issues
- `ERROR`: Error conditions
- `CRITICAL`: Severe errors

---

## Reporting

### HTML Reports

Reports are automatically generated at `reports/report.html` after each test run.

**Report Features:**
- Test pass/fail status
- Execution time
- Embedded screenshots
- Log output

**View Report:**
```bash
# Windows
start reports/report.html

# Linux
xdg-open reports/report.html

# Mac
open reports/report.html
```

---

## Screenshots

Screenshots are captured automatically:
- **Location:** `screenshots/` directory
- **Naming Convention:** `{test_name}_{YYYYMMDD_HHMMSS}.png`
- **Timing:** Captured after each test (pass or fail)
- **Integration:** Embedded in HTML reports

---

## Best Practices

### 1. Page Object Model
- Keep locators and actions in page classes
- Use meaningful method names
- Inherit from `BasePage` for common functionality

### 2. Test Organization
- One test class per feature/module
- Clear test method names describing the scenario
- Use pytest markers for categorization

### 3. Logging
- Log important actions and validations
- Use appropriate log levels
- Include relevant context in log messages

### 4. Wait Strategies
- Implicit wait: Set in `BasePage` (10 seconds)
- Explicit wait: Use `WebDriverWait` for specific elements
- Avoid hard-coded `time.sleep()`

### 5. Configuration Management
- Keep device capabilities in `config/desired_caps.py`
- Use environment variables for sensitive data
- Maintain separate configs for different environments

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Appium not found" | Ensure Appium is installed globally and in PATH |
| "Port 4725 already in use" | Framework auto-kills existing server; check firewall |
| "Device not found" | Verify device connection with `adb devices` |
| "Session not created" | Check UiAutomator2 driver is installed |
| "Element not found" | Increase wait time or check locator strategy |

### Verify Setup
```bash
# Check Appium installation
appium --version

# Check drivers
appium driver list

# Check connected devices
adb devices

# Check Android SDK
echo %ANDROID_HOME%
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

---

## License

This project is available for educational and professional use.

---

## Author

n.beshra

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Current | Initial framework with basic test scenarios |