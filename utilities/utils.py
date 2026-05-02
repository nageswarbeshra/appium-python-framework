import getpass
import os
import re
import subprocess
import time
import urllib.request
import urllib.error
import platform
import psutil
from appium import webdriver
from appium.options.android import UiAutomator2Options
import config
from utilities.log_handler import nowLogs


class Utils:
    def __init__(self):
        self.driver = None
        self.appium_process = None
        self.appium_log_file = None

    def is_port_in_use(self, port):
        """Check if the specified port is in use and return the PID if found."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return conn.pid
            return None
        except Exception as e:
            nowLogs(f"Error checking port {port}: {str(e)}")
            return None

    def _find_appium_on_windows(self):
        """Find Appium executable on Windows using multiple methods."""
        
        # Debug: Log environment information
        nowLogs(f"DEBUG: Current user: {os.environ.get('USERNAME', 'unknown')}")
        nowLogs(f"DEBUG: USERPROFILE: {os.environ.get('USERPROFILE', 'not set')}")
        nowLogs(f"DEBUG: APPDATA: {os.environ.get('APPDATA', 'not set')}")
        nowLogs(f"DEBUG: PATH: {os.environ.get('PATH', 'not set')[:500]}...")

        # pc_username = getpass.getuser()
        # appium_path = f"C:\\Users\\" + pc_username + "\\AppData\\Roaming\\npm\\appium"
        # if appium_path and os.path.exists(appium_path):
        #     nowLogs(f"Appium found via APPIUM_PATH environment variable: {appium_path}")
        #     return appium_path

        # Method 1: Check APPIUM_PATH environment variable
        user_ = os.environ.get('USERNAME')
        formatted_name = re.sub(r'\d*\$$', '', user_).replace('-', '.').lower()
        appium_path = f"C:\\Users\\" + formatted_name + "\\AppData\\Roaming\\npm\\appium"
        if appium_path and os.path.exists(appium_path):
            nowLogs(f"Appium found via APPIUM_PATH environment variable: {appium_path}")
            return appium_path
        #
        # Method 2: Use 'where' command
        try:
            result = subprocess.run(
                "where appium",
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0 and result.stdout.strip():
                appium_path = result.stdout.strip().split('\n')[0].strip()
                if appium_path and os.path.exists(appium_path):
                    nowLogs(f"Appium found via 'where' command: {appium_path}")
                    return appium_path
        except Exception as e:
            nowLogs(f"'where' command failed: {str(e)}")
        
        # Method 3: Check common npm global installation paths on Windows
        # Include paths for different user contexts (current user, SYSTEM, all users)
        common_paths = []
        
        # Current user's AppData
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            common_paths.append(os.path.join(appdata, 'npm', 'appium.cmd'))
            common_paths.append(os.path.join(appdata, 'npm', 'appium'))
        
        # User profile based paths
        userprofile = os.environ.get('USERPROFILE', '')
        if userprofile:
            common_paths.append(os.path.join(userprofile, 'AppData', 'Roaming', 'npm', 'appium.cmd'))
            common_paths.append(os.path.join(userprofile, 'AppData', 'Roaming', 'npm', 'appium'))
        
        # System-wide paths
        common_paths.extend([
            os.path.join('C:', 'Program Files', 'nodejs', 'appium.cmd'),
            os.path.join('C:', 'Program Files (x86)', 'nodejs', 'appium.cmd'),
            'C:\\Program Files\\nodejs\\appium.cmd',
            'C:\\Program Files (x86)\\nodejs\\appium.cmd',
        ])
        
        # Check common user profiles for Jenkins agents
        common_user_profiles = [
            'C:\\Users\\Administrator',
            'C:\\Users\\Public',
            'C:\\Windows\\ServiceProfiles\\LocalService',
            'C:\\Windows\\ServiceProfiles\\NetworkService',
        ]
        
        # Also check if we can find user profiles from existing paths
        for profile in common_user_profiles:
            common_paths.append(os.path.join(profile, 'AppData', 'Roaming', 'npm', 'appium.cmd'))
            common_paths.append(os.path.join(profile, 'AppData', 'Roaming', 'npm', 'appium'))
        
        # Also check PATH directories directly
        path_env = os.environ.get('PATH', '')
        for path_dir in path_env.split(os.pathsep):
            if path_dir:
                for ext in ['.cmd', '.exe', '']:
                    potential_path = os.path.join(path_dir, 'appium' + ext)
                    if potential_path not in common_paths:
                        common_paths.append(potential_path)
        
        nowLogs(f"DEBUG: Checking {len(common_paths)} potential paths for Appium...")
        
        for path in common_paths:
            if path and os.path.exists(path):
                nowLogs(f"Appium found at: {path}")
                return path
        
        # Method 4: Try to find via npm root
        try:
            result = subprocess.run(
                "npm root -g",
                capture_output=True,
                text=True,
                shell=True
            )
            nowLogs(f"DEBUG: npm root -g output: {result.stdout.strip()}, stderr: {result.stderr.strip()}")
            if result.returncode == 0 and result.stdout.strip():
                npm_root = result.stdout.strip()
                appium_path = os.path.join(npm_root, '.bin', 'appium.cmd')
                if os.path.exists(appium_path):
                    nowLogs(f"Appium found via npm root: {appium_path}")
                    return appium_path
                # Also try without .cmd extension
                appium_path = os.path.join(npm_root, '.bin', 'appium')
                if os.path.exists(appium_path):
                    nowLogs(f"Appium found via npm root: {appium_path}")
                    return appium_path
        except Exception as e:
            nowLogs(f"npm root command failed: {str(e)}")
        
        nowLogs("=" * 60)
        nowLogs("ERROR: Appium not found in any known location!")
        nowLogs("=" * 60)
        nowLogs("SOLUTIONS:")
        nowLogs("1. Set APPIUM_PATH environment variable in Jenkins to the full path of appium.cmd")
        nowLogs("2. Or add npm directory to PATH in Jenkins configuration")
        nowLogs("3. Or install Appium globally: npm install -g appium")
        nowLogs("=" * 60)
        return None

    def stop_existing_appium_server(self, port=4723):
        """Stop any existing Appium server on the specified port and wait until port is free."""
        try:
            max_wait_time = 90
            start_time = time.time()
            port_free = False
            retry_interval = 5
            is_windows = platform.system() == "Windows"

            while time.time() - start_time < max_wait_time and not port_free:
                pid = self.is_port_in_use(port)
                if pid is None:
                    nowLogs(f"Port {port} is free.")
                    return True

                nowLogs(f"Port {port} is in use by PID {pid}. Attempting to stop...")
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                    nowLogs(f"Process name: {process_name}")
                    if 'node' in process_name.lower():
                        if is_windows:
                            result = subprocess.run(
                                ['taskkill', '/PID', str(pid), '/F'],
                                capture_output=True,
                                text=True
                            )
                            nowLogs(f"taskkill output for PID {pid}: {result.stdout}")
                        else:
                            result = subprocess.run(
                                ['kill', '-9', str(pid)],
                                capture_output=True,
                                text=True
                            )
                            nowLogs(f"kill output for PID {pid}: {result.stdout}")
                        time.sleep(2)
                    else:
                        nowLogs(f"Skipping termination of non-Node.js process: {process_name}")
                except (psutil.NoSuchProcess, subprocess.CalledProcessError) as e:
                    nowLogs(f"Failed to terminate process with PID {pid}: {str(e)}")

                if self.is_port_in_use(port) is None:
                    nowLogs(f"Port {port} is now free after termination.")
                    port_free = True
                else:
                    nowLogs(f"Port {port} is still in use. Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)

            if not port_free:
                nowLogs(f"Error: Port {port} is still in use after maximum wait time.")
                return False
            return True
        except Exception as e:
            nowLogs(f"Error checking or stopping existing server: {str(e)}")
            return False

    def start_appium_server(self, port=4723):
        """Start Appium server programmatically with a dynamic user path."""
        is_windows = platform.system() == "Windows"

        # Check for APPIUM_PATH environment variable first (useful for Jenkins)
        appium_path = os.environ.get('APPIUM_PATH')
        
        if appium_path and os.path.exists(appium_path):
            nowLogs(f"Using APPIUM_PATH from environment: {appium_path}")
        elif is_windows:
            appium_path = self._find_appium_on_windows()
            if appium_path is None:
                nowLogs("ERROR: Appium not found. Please install Appium or set APPIUM_PATH environment variable.")
                return False
        else:
            appium_path = "appium"

        log_file_path = os.path.join("logs", "appium.log")
        os.makedirs("logs", exist_ok=True)

        try:
            # When using shell=True, command must be a string; when shell=False, use a list
            if is_windows:
                result = subprocess.run(f'"{appium_path}" --version', capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run([appium_path, '--version'], capture_output=True, text=True)
            nowLogs(f"Appium version: {result.stdout.strip()}")
            if result.returncode != 0:
                nowLogs(f"Appium version check failed with error: {result.stderr}")
                return False
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            nowLogs(f"Error: Appium not found at {appium_path}. Error: {str(e)}")
            return False

        if not self.stop_existing_appium_server(port):
            return False

        try:
            nowLogs(f"Starting new Appium server on port {port}...")
            self.appium_log_file = open(log_file_path, 'w')

            # When using shell=True, command must be a string; when shell=False, use a list
            if is_windows:
                appium_cmd = f'"{appium_path}" --address 127.0.0.1 --port {port} --log-level debug'
                self.appium_process = subprocess.Popen(
                    appium_cmd,
                    stdout=None,  # Show logs in terminal
                    stderr=None,
                    universal_newlines=True,
                    shell=True
                )
            else:
                self.appium_process = subprocess.Popen(
                    [appium_path, '--address', '127.0.0.1', '--port', str(port), '--log-level', 'debug'],
                    stdout=None,  # Show logs in terminal
                    stderr=None,
                    universal_newlines=True
                )

            # Health check loop
            max_wait_time = 60
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/status', timeout=2) as response:
                        if response.getcode() == 200:
                            nowLogs(f"Appium server started successfully on port {port}")
                            return True
                except Exception:
                    time.sleep(2)

            raise Exception("Appium server failed to start within time limit")
        except Exception as e:
            nowLogs(f"Failed to start Appium server: {str(e)}")
            self.stop_appium_server()
            return False

    def stop_appium_server(self):
        """Stop the Appium server if running."""
        if self.appium_process:
            nowLogs("Stopping Appium server...")
            try:
                self.appium_process.terminate()
                self.appium_process.wait(timeout=5)
                nowLogs("Appium server stopped successfully")
            except subprocess.TimeoutExpired:
                nowLogs("Appium server did not terminate gracefully, forcing kill...")
                self.appium_process.kill()
                self.appium_process.wait()
            except Exception as e:
                nowLogs(f"Error stopping Appium server: {str(e)}")
            self.appium_process = None
        if self.appium_log_file:
            self.appium_log_file.close()
            self.appium_log_file = None

    def setup_module(self,app_name):
        # """Set up Appium driver with device-specific capabilities.""" com.samsung.android.dialer  com.samsung.android.dialer.DialtactsActivity
        """ "appPackage": f"{appPackage}",
                "appActivity": f"{appActivity}","""
        app = config.APPS[app_name]
        try:

            desired_cap = {
                "appium:platformName": "Android",
                "appium:deviceName": config.DEVICE_NAME,
                "appium:automationName": "UiAutomator2",
                "appium:appPackage": app["package"],
                "appium:appActivity": app["activity"],
                "appium:autoGrantPermissions": True
            }



            nowLogs(f"Using capabilities: {desired_cap}")
            capability_options = UiAutomator2Options().load_capabilities(desired_cap)
            self.driver = webdriver.Remote(config.APPIUM_SERVER, options=capability_options)
            nowLogs("Appium driver initialized successfully")
            return self.driver
        except Exception as e:
            nowLogs(f"Failed to set up Appium driver: {str(e)}")
            self.stop_appium_server()
            raise


    def teardown_module(self):
        """Tear down Appium driver and server."""
        if self.driver:
            nowLogs("Quitting Appium driver...")
            try:
                self.driver.quit()
            except Exception as e:
                nowLogs(f"Error quitting driver: {str(e)}")
            self.driver = None
        self.stop_appium_server()
