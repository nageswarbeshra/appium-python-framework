import os
import datetime
import pytest
import pytest_html

from utilities.driver_factory import get_driver
from utilities.utils import Utils

# ----------------------------------------------------------------------
# Fix Android SDK environment variables if not set correctly
# ----------------------------------------------------------------------
def _fix_android_sdk_env():
    """Ensure ANDROID_HOME and ANDROID_SDK_ROOT point to the correct SDK path."""
    correct_sdk_path = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Android', 'Sdk')
    
    # Check if current ANDROID_HOME is incorrect or not set
    current_android_home = os.environ.get('ANDROID_HOME', '')
    if not current_android_home or 'Android Studio' in current_android_home or not os.path.exists(current_android_home):
        if os.path.exists(correct_sdk_path):
            os.environ['ANDROID_HOME'] = correct_sdk_path
            os.environ['ANDROID_SDK_ROOT'] = correct_sdk_path
            print(f"Fixed ANDROID_HOME to: {correct_sdk_path}")

# Fix Android SDK environment at module load time
_fix_android_sdk_env()

port = 4723
# ----------------------------------------------------------------------
# Session‑scoped fixture: start Appium server once for the whole test run
# ----------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def appium_server():
    """Start Appium server at the beginning of the session and stop it at the end."""
    utils = Utils()

    utils.start_appium_server(port=port)
    yield utils
    utils.stop_appium_server()


# ----------------------------------------------------------------------
# Function‑scoped fixture: provide a driver instance for each test
# ----------------------------------------------------------------------
@pytest.fixture()
def driver(request, appium_server):
    """Create a driver using the already‑started Appium server."""

    drv = get_driver(port)
    yield drv

    # ------------------------------------------------------------------
    # Capture screenshot (even on failure) and store path in the test node
    # ------------------------------------------------------------------
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name
        screenshot_path = os.path.join(
            screenshots_dir, f"{test_name}_{timestamp}.png"
        )
        drv.save_screenshot(screenshot_path)
        # Store the path for later use in the HTML report hook
        request.node.screenshot_path = screenshot_path
        print(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")

    # ------------------------------------------------------------------
    # Quit the driver
    # ------------------------------------------------------------------
    if drv:
        drv.quit()


# ----------------------------------------------------------------------
# Pytest hook: embed screenshot into HTML report (pytest‑html plugin)
# ----------------------------------------------------------------------
def pytest_runtest_makereport(item, call):
    """Attach the screenshot to the HTML report (including failures)."""
    # Execute only after the test call phase
    if call.when != "call":
        return

    # Import pytest_html lazily
    try:
        import pytest_html  # noqa: F401
    except ImportError:
        return

    # Retrieve the report object
    report = call.result if hasattr(call, "result") else getattr(call, "get_result", lambda: None)()
    if report is None:
        return

    screenshot_path = getattr(item, "screenshot_path", None)
    if screenshot_path and os.path.exists(screenshot_path):
        extra = getattr(report, "extra", [])
        extra.append(pytest_html.extras.image(screenshot_path))
        report.extra = extra


# ----------------------------------------------------------------------
# Optional: make pytest‑html available without importing it directly
# ----------------------------------------------------------------------
def pytest_configure(config):
    """Register the pytest‑html plugin if it is installed."""
    try:
        import pytest_html  # noqa: F401
    except ImportError:
        # pytest‑html is not installed; tests will still run without HTML reports
        pass