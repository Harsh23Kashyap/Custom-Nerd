# === Custom-Nerd/Nerd-Engine WSL Presetup (Windows Only) ===
# For: Windows users preparing WSL2/Ubuntu before running setup.py.

import os
import sys
import subprocess
import platform
import datetime
import re
from pathlib import Path

# ------------------------------------------------------------------------------------
# Windows WSL2 Setup Script
# 
# This script is specifically for Windows users to set up WSL2 and Ubuntu
# BEFORE running setup.py. This ensures that setup.py can assume WSL2 is
# already configured and ready to use.
#
# Run this script FIRST on Windows, then proceed with setup.py
# ------------------------------------------------------------------------------------

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    MAGENTA = '\033[95m'

def display_manual_instructions(logger, title, steps, color=Colors.CYAN):
    """Display beautiful, prominent manual instructions."""
    logger.log("", Colors.RESET)
    logger.log("╔" + "═" * 68 + "╗", Colors.BOLD + color)
    logger.log("║" + " " * 20 + title + " " * (48 - len(title)) + "║", Colors.BOLD + color)
    logger.log("╚" + "═" * 68 + "╝", Colors.BOLD + color)
    logger.log("", Colors.RESET)
    
    for i, step in enumerate(steps, 1):
        if isinstance(step, dict):
            step_title = step.get('title', f'Step {i}')
            step_commands = step.get('commands', [])
            step_notes = step.get('notes', [])
            
            logger.log(f"   {Colors.BOLD}{Colors.YELLOW}{i}️⃣  {step_title}{Colors.RESET}", Colors.RESET)
            if step_commands:
                for cmd in step_commands:
                    logger.log(f"      {Colors.BOLD}{Colors.GREEN}→{Colors.RESET} {Colors.CYAN}{cmd}{Colors.RESET}", Colors.RESET)
            if step_notes:
                for note in step_notes:
                    logger.log(f"      {Colors.YELLOW}•{Colors.RESET} {note}", Colors.RESET)
        else:
            logger.log(f"   {Colors.BOLD}{Colors.YELLOW}{i}️⃣  {step}{Colors.RESET}", Colors.RESET)
        logger.log("", Colors.RESET)
    
    logger.log("╔" + "═" * 68 + "╗", Colors.BOLD + Colors.MAGENTA)
    logger.log("║" + " " * 15 + "⚠️  READ THE STEPS ABOVE CAREFULLY ⚠️" + " " * 15 + "║", Colors.BOLD + Colors.MAGENTA)
    logger.log("╚" + "═" * 68 + "╝", Colors.BOLD + Colors.MAGENTA)
    logger.log("", Colors.RESET)

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_cmd(cmd_list, logger=None):
    """
    Run command and return (exit_code, combined_output).
    Handles UTF-16LE encoding issues on Windows ARM64 (UTM).
    """
    try:
        # Handling WSL's specific UTF-16LE encoding on Windows ARM64
        process = subprocess.run(cmd_list, capture_output=True, text=True, encoding='utf-16le', errors='ignore')
        output = process.stdout + process.stderr
        if not output.strip():
            # Fallback to default encoding if UTF-16LE doesn't work
            process = subprocess.run(cmd_list, capture_output=True, text=True, errors='ignore')
            output = process.stdout + process.stderr
        # Clean null bytes that sometimes appear in WSL output
        return process.returncode, output.replace('\x00', '')
    except Exception as e:
        if logger:
            # Format error message nicely - show command as readable string instead of list
            if isinstance(e, subprocess.CalledProcessError):
                cmd_str = " ".join(e.cmd) if isinstance(e.cmd, list) else str(e.cmd)
                error_msg = f"Command '{cmd_str}' returned non-zero exit status {e.returncode}"
                logger.log(f"⚠️ {error_msg}", Colors.YELLOW)
            else:
                logger.log(f"⚠️ Error running command: {e}", Colors.YELLOW)
        return -1, str(e)

def setup_wsl_user(logger, username, password):
    """Automatically injects the user and password into the Ubuntu instance."""
    logger.log(f"👤 Creating user '{username}' inside Ubuntu...", Colors.CYAN)
    
    # Create the user with sudo privileges and a home directory
    create_user_cmd = ["wsl", "-d", "Ubuntu", "useradd", "-m", "-G", "sudo", "-s", "/bin/bash", username]
    run_cmd(create_user_cmd, logger)
    
    # Automatically set the password via the chpasswd pipe to avoid interactive prompts
    set_pw_cmd = ["wsl", "-d", "Ubuntu", "sh", "-c", f"echo '{username}:{password}' | chpasswd"]
    run_cmd(set_pw_cmd, logger)
    
    # Configure WSL to always log in as this new user by default
    logger.log("⚙️ Setting default WSL user...", Colors.CYAN)
    # Note: On some versions, 'config' is replaced by 'wsl.exe --user' flag usage
    run_cmd(["powershell", "-Command", f"ubuntu config --default-user {username}"], logger)

def run_command_with_output(cmd, logger, timeout=None, description=""):
    """
    Run a subprocess command and display output in real-time with [Internal Check] prefix.
    Returns: (returncode, stdout, stderr)
    """
    import subprocess
    import threading
    import queue
    import re
    
    if description:
        logger.log(f"   {description}", Colors.CYAN)
    
    # Show the command being run with visual separator
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
    logger.log("", Colors.RESET)
    logger.log("   " + "─" * 70, Colors.CYAN)
    logger.log(f"   {Colors.CYAN}┌─ [Internal Check] ────────────────────────────────────────────────┐{Colors.RESET}", Colors.RESET)
    logger.log(f"   {Colors.CYAN}│{Colors.RESET} Running: {cmd_str}", Colors.RESET)
    logger.log(f"   {Colors.CYAN}└──────────────────────────────────────────────────────────────────┘{Colors.RESET}", Colors.RESET)
    logger.log("", Colors.RESET)
    
    # Check if this is a DISM command (to filter progress bars)
    is_dism = isinstance(cmd, list) and len(cmd) > 0 and 'dism' in cmd[0].lower()
    
    def is_dism_progress_line(line):
        """Check if a line is a DISM progress bar that should be filtered."""
        if not is_dism:
            return False
        line_stripped = line.strip()
        # Filter out progress bar lines: [=====...=====] with percentages
        if re.match(r'^\s*\[[=\s]*\d+\.\d+%[=\s]*\]\s*$', line_stripped):
            return True
        # Filter out lines that are just progress bars with brackets and equals signs
        if re.match(r'^\s*\[[=\s\-]+\]\s*$', line_stripped):
            return True
        # Filter out lines that are mostly brackets, equals, and spaces
        if re.match(r'^\s*\[[=\s\-]*\]\s*$', line_stripped) and len(line_stripped) > 20:
            return True
        return False
    
    def should_display_line(line):
        """Determine if a line should be displayed (filter DISM progress bars)."""
        if is_dism_progress_line(line):
            return False
        # Show important DISM messages
        if is_dism:
            line_lower = line.lower()
            # Show important messages
            important_keywords = [
                'deployment image servicing',
                'image version',
                'enabling feature',
                'operation completed',
                'error',
                'failed',
                'success',
                'warning',
                'access is denied',
                'administrator'
            ]
            if any(keyword in line_lower for keyword in important_keywords):
                return True
            # Show non-empty lines that aren't progress bars
            if line.strip() and not is_dism_progress_line(line):
                return True
            return False
        return True
    
    stdout_lines = []
    stderr_lines = []
    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()
    
    def read_output(pipe, queue_obj, lines_list):
        """Read from pipe and put lines in queue and list."""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    lines_list.append(line)
                    queue_obj.put(line)
            queue_obj.put(None)  # Signal end
        except Exception:
            queue_obj.put(None)
        finally:
            pipe.close()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, stdout_queue, stdout_lines))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, stderr_queue, stderr_lines))
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Display output in real-time
        stdout_done = False
        stderr_done = False
        import time
        last_progress_time = time.time() if is_dism else 0
        progress_interval = 15  # Show progress message every 15 seconds for DISM
        
        while not (stdout_done and stderr_done):
            # For DISM commands, show periodic progress updates
            if is_dism and not stdout_done:
                current_time = time.time()
                if current_time - last_progress_time >= progress_interval:
                    logger.log(f"   {Colors.CYAN}│{Colors.RESET} ⏳ Still processing... (this may take 2-5 minutes)", Colors.RESET)
                    last_progress_time = current_time
            # Check stdout
            try:
                line = stdout_queue.get_nowait()
                if line is None:
                    stdout_done = True
                else:
                    # Filter DISM progress bars and only show important messages
                    if should_display_line(line):
                        # Indent internal check output for visual distinction
                        logger.log(f"   {Colors.CYAN}│{Colors.RESET} {line.rstrip()}", Colors.RESET)
            except queue.Empty:
                pass
            
            # Check stderr
            try:
                line = stderr_queue.get_nowait()
                if line is None:
                    stderr_done = True
                else:
                    # Filter DISM progress bars and only show important messages
                    if should_display_line(line):
                        # Indent internal check stderr output (errors/warnings)
                        logger.log(f"   {Colors.CYAN}│{Colors.YELLOW} {line.rstrip()}{Colors.RESET}", Colors.RESET)
            except queue.Empty:
                pass
            
            # Check if process is done
            if process.poll() is not None:
                # Process finished, read remaining output
                import time
                time.sleep(0.1)  # Give threads time to finish reading
                # Drain remaining queues
                while True:
                    try:
                        line = stdout_queue.get_nowait()
                        if line is None:
                            stdout_done = True
                            break
                        # Filter DISM progress bars
                        if should_display_line(line):
                            logger.log(f"   {Colors.CYAN}│{Colors.RESET} {line.rstrip()}", Colors.RESET)
                    except queue.Empty:
                        break
                
                while True:
                    try:
                        line = stderr_queue.get_nowait()
                        if line is None:
                            stderr_done = True
                            break
                        # Filter DISM progress bars
                        if should_display_line(line):
                            logger.log(f"   {Colors.CYAN}│{Colors.RESET} {Colors.YELLOW}{line.rstrip()}{Colors.RESET}", Colors.RESET)
                    except queue.Empty:
                        break
                break
            
            import time
            time.sleep(0.05)  # Small delay to avoid busy waiting
        
        # Wait for process to complete
        returncode = process.wait(timeout=timeout)
        
        # Wait for threads to finish
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        
        stdout = ''.join(stdout_lines)
        stderr = ''.join(stderr_lines)
        
        # Close the visual box
        logger.log("", Colors.RESET)
        status_color = Colors.GREEN if returncode == 0 else Colors.RED
        status_icon = "✓" if returncode == 0 else "✗"
        logger.log(f"   {Colors.CYAN}┌─ [Internal Check] Result ─────────────────────────────────────────┐{Colors.RESET}", Colors.RESET)
        logger.log(f"   {Colors.CYAN}│{Colors.RESET} {status_icon} Exit code: {status_color}{returncode}{Colors.RESET}", Colors.RESET)
        logger.log(f"   {Colors.CYAN}└──────────────────────────────────────────────────────────────────┘{Colors.RESET}", Colors.RESET)
        logger.log("", Colors.RESET)
        
        return returncode, stdout, stderr
        
    except subprocess.TimeoutExpired:
        process.kill()
        logger.log(f"   {Colors.CYAN}┌─ [Internal Check] Error ──────────────────────────────────────────┐{Colors.RESET}", Colors.RESET)
        logger.log(f"   {Colors.CYAN}│{Colors.RESET} ✗ Command timed out after {timeout} seconds", Colors.RESET)
        logger.log(f"   {Colors.CYAN}└──────────────────────────────────────────────────────────────────┘{Colors.RESET}", Colors.RESET)
        logger.log("", Colors.RESET)
        return -1, ''.join(stdout_lines), ''.join(stderr_lines)
    except Exception as e:
        logger.log(f"   {Colors.CYAN}┌─ [Internal Check] Error ──────────────────────────────────────────┐{Colors.RESET}", Colors.RESET)
        # Format error message nicely - show command as readable string instead of list
        if isinstance(e, subprocess.CalledProcessError):
            cmd_str = " ".join(e.cmd) if isinstance(e.cmd, list) else str(e.cmd)
            error_msg = f"Command '{cmd_str}' returned non-zero exit status {e.returncode}"
            logger.log(f"   {Colors.CYAN}│{Colors.RESET} ✗ {error_msg}", Colors.RESET)
        else:
            logger.log(f"   {Colors.CYAN}│{Colors.RESET} ✗ Error running command: {e}", Colors.RESET)
        logger.log(f"   {Colors.CYAN}└──────────────────────────────────────────────────────────────────┘{Colors.RESET}", Colors.RESET)
        logger.log("", Colors.RESET)
        return -1, ''.join(stdout_lines), ''.join(stderr_lines)

class Logger:
    def __init__(self, log_file_path):
        self.log_file = open(log_file_path, "w", encoding='utf-8')
        self.log_file.write(f"Presetup Log - Started at {datetime.datetime.now()}\n")
        self.log_file.write("="*50 + "\n")
        
        # Enable ANSI colors on Windows 10+ if available
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # Enable ANSI escape sequence processing
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass  # If it fails, colors won't work but script will continue
        
    def log(self, text, color=None, end='\n'):
        # Print to console
        # If text already contains color codes, use them directly
        # Otherwise, apply the color parameter
        if color and Colors.CYAN not in text and Colors.YELLOW not in text and Colors.RED not in text and Colors.GREEN not in text:
            # Text doesn't have embedded colors, apply the color parameter
            if platform.system() != "Windows":
                print(f"{color}{text}{Colors.RESET}", end=end)
            else:
                # On Windows, try to use colors (enabled in __init__)
                print(f"{color}{text}{Colors.RESET}", end=end)
        else:
            # Text has embedded colors or no color specified
            print(text, end=end)

        # Write to file (always strip ANSI codes for file)
        clean_text = strip_ansi(text)
        if end == '\n':
             timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
             self.log_file.write(f"{timestamp}{clean_text}\n")
        else:
             self.log_file.write(clean_text)
        self.log_file.flush()
    
    def raw_log(self, text):
        clean_text = strip_ansi(text)
        self.log_file.write(clean_text)
        self.log_file.flush()

    def close(self):
        self.log_file.write("\n" + "="*50 + "\n")
        self.log_file.write(f"Presetup Log - Finished at {datetime.datetime.now()}\n")
        self.log_file.close()

def check_wsl_catastrophic_failure(logger, distro="Ubuntu"):
    """Check if WSL is experiencing catastrophic failure errors."""
    try:
        result = subprocess.run(
            ["wsl", "-d", distro, "echo", "test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check for catastrophic failure error messages
        error_output = result.stderr.lower() if result.stderr else ""
        stdout_output = result.stdout.lower() if result.stdout else ""
        combined_output = error_output + stdout_output
        
        if ("catastrophic failure" in combined_output or 
            "e_unexpected" in combined_output or
            "wsl/service" in combined_output):
            return True
        
        # Also check return code - catastrophic failures often return non-zero
        if result.returncode != 0 and ("catastrophic" in combined_output or "unexpected" in combined_output):
            return True
            
        return False
    except Exception:
        # If we can't even run the command, it might be a catastrophic failure
        return True

def check_ubuntu_setup_complete(logger, distro="Ubuntu"):
    """Check if Ubuntu WSL has completed initial user setup."""
    try:
        # First check for catastrophic failure
        if check_wsl_catastrophic_failure(logger, distro):
            logger.log("❌ WSL is experiencing a catastrophic failure error.", Colors.RED)
            logger.log("", Colors.RESET)
            logger.log("📋 This usually means Ubuntu needs to be unregistered and reinstalled:", Colors.CYAN)
            logger.log("", Colors.RESET)
            logger.log("   1. Run: wsl --unregister Ubuntu", Colors.YELLOW)
            logger.log("   2. Run: wsl --install -d Ubuntu", Colors.YELLOW)
            logger.log("   3. After Ubuntu launches, create your username and password", Colors.YELLOW)
            logger.log("   4. Run this script again", Colors.YELLOW)
            logger.log("", Colors.RESET)
            return False
        
        result = subprocess.run(
            ["wsl", "-d", distro, "whoami"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check stderr for catastrophic failure messages
        error_output = result.stderr.lower() if result.stderr else ""
        if "catastrophic failure" in error_output or "e_unexpected" in error_output:
            logger.log("❌ WSL is experiencing a catastrophic failure error.", Colors.RED)
            logger.log("", Colors.RESET)
            logger.log("📋 This usually means Ubuntu needs to be unregistered and reinstalled:", Colors.CYAN)
            logger.log("", Colors.RESET)
            logger.log("   1. Run: wsl --unregister Ubuntu", Colors.YELLOW)
            logger.log("   2. Run: wsl --install -d Ubuntu", Colors.YELLOW)
            logger.log("   3. After Ubuntu launches, create your username and password", Colors.YELLOW)
            logger.log("   4. Run this script again", Colors.YELLOW)
            logger.log("", Colors.RESET)
            return False
        
        if result.returncode == 0 and result.stdout.strip():
            username = result.stdout.strip()
            logger.log(f"✅ Ubuntu setup complete (user: {username})", Colors.GREEN)
            return True
        else:
            logger.log("⚠️ Ubuntu appears to be installed but user setup may be incomplete", Colors.YELLOW)
            return False
    except subprocess.TimeoutExpired:
        logger.log("⏱️ Ubuntu is responding slowly. It may be waiting for initial setup.", Colors.YELLOW)
        return False
    except Exception as e:
        error_str = str(e).lower()
        # Check if the exception message contains catastrophic failure indicators
        if "catastrophic" in error_str or "e_unexpected" in error_str:
            logger.log("❌ WSL is experiencing a catastrophic failure error.", Colors.RED)
            logger.log("", Colors.RESET)
            logger.log("📋 This usually means Ubuntu needs to be unregistered and reinstalled:", Colors.CYAN)
            logger.log("", Colors.RESET)
            logger.log("   1. Run: wsl --unregister Ubuntu", Colors.YELLOW)
            logger.log("   2. Run: wsl --install -d Ubuntu", Colors.YELLOW)
            logger.log("   3. After Ubuntu launches, create your username and password", Colors.YELLOW)
            logger.log("   4. Run this script again", Colors.YELLOW)
            logger.log("", Colors.RESET)
            return False
        logger.log(f"⚠️ Could not verify Ubuntu setup: {e}", Colors.YELLOW)
        return False

def check_wsl_installed(logger):
    """Check if WSL2 is installed and available."""
    try:
        result = subprocess.run(
            ["wsl", "--status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.log("✅ WSL is installed", Colors.GREEN)
            
            # Check for Ubuntu distribution
            list_result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Check WSL version
            if "2" in list_result.stdout or "VERSION" in list_result.stdout:
                logger.log("✅ WSL2 is configured", Colors.GREEN)
            else:
                logger.log("⚠️ WSL1 detected. Upgrading to WSL2...", Colors.YELLOW)
                try:
                    subprocess.run(
                        ["wsl", "--set-default-version", "2"],
                        capture_output=True,
                        timeout=10
                    )
                    logger.log("✅ Set WSL2 as default version", Colors.GREEN)
                except Exception as e:
                    logger.log(f"⚠️ Could not set WSL2 as default: {e}", Colors.YELLOW)
            
            # Get the exact Ubuntu distribution name
            ubuntu_distro = get_ubuntu_distro_name(logger)
            
            if ubuntu_distro:
                logger.log(f"✅ Ubuntu distribution found: {ubuntu_distro}", Colors.GREEN)
                
                # Check if Ubuntu setup is complete using the exact name
                if check_ubuntu_setup_complete(logger, ubuntu_distro):
                    return True, ubuntu_distro, True  # (wsl_installed, distro, ready)
                else:
                    return True, ubuntu_distro, False  # Installed but not ready
            else:
                logger.log("⚠️ Ubuntu distribution not found", Colors.YELLOW)
                return True, None, False  # WSL installed but no Ubuntu
        return False, None, False
    except FileNotFoundError:
        logger.log("❌ WSL is not installed", Colors.RED)
        return False, None, False
    except Exception as e:
        logger.log(f"⚠️ Error checking WSL: {e}", Colors.YELLOW)
        return False, None, False

def check_admin_privileges():
    """Check if the script is running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_ubuntu_distro_name(logger, wsl_list_output=None):
    """Extract the exact Ubuntu distribution name from WSL list."""
    try:
        if not wsl_list_output:
            result = subprocess.run(["wsl", "--list", "--verbose"], capture_output=True, text=True, timeout=10)
            wsl_list_output = result.stdout
        
        # CRITICAL: WSL output often contains null bytes (\x00) on ARM64/UTM
        clean_output = wsl_list_output.replace('\x00', '')
        lines = clean_output.strip().splitlines()
        
        for line in lines:
            line_lower = line.lower().strip()
            # Look for 'ubuntu' and ignore the header row
            if 'ubuntu' in line_lower and 'name' not in line_lower:
                # Remove asterisk and extract name
                parts = line.replace('*', '').split()
                if parts:
                    distro_name = parts[0]
                    logger.log(f"📋 Found Ubuntu distribution: {distro_name}", Colors.CYAN)
                    return distro_name
        return None
    except Exception as e:
        logger.log(f"⚠️ Could not determine Ubuntu distribution name: {e}", Colors.YELLOW)
        return None

def install_wsl_logic(logger):
    """Refined installation logic to handle UTM/WSL1 fallback automatically."""
    logger.log("Step 4/4: Installing Ubuntu...", Colors.BLUE)
    
    # Try WSL2 first
    logger.log("⏳ Attempting WSL2 installation...", Colors.CYAN)
    rc, stdout, stderr = run_command_with_output(["wsl", "--install", "-d", "Ubuntu"], logger, timeout=600)
    
    error_out = (stdout + stderr).lower()
    combined_output = (stdout + stderr).lower()
    
    # Check if WSL2 is physically impossible (like in your UTM setup)
    is_wsl2_error = (
        "hcs_e_hyperv_not_installed" in (stdout + stderr) or
        "wsl2 is not supported" in (stdout + stderr) or
        "wsl2 is not supported" in combined_output
    )
    
    if is_wsl2_error and rc != 0:
        logger.log("\n⚠️ WSL2 is not supported by your current hardware/VM settings.", Colors.YELLOW)
        logger.log("💡 Automatically falling back to WSL1...", Colors.GREEN)
        
        # Force WSL1
        logger.log("   Setting WSL1 as default version...", Colors.CYAN)
        wsl1_set_rc, _, _ = run_command_with_output(["wsl", "--set-default-version", "1"], logger, timeout=60)
        
        logger.log("   Installing Ubuntu with WSL1...", Colors.CYAN)
        wsl1_rc, wsl1_stdout, wsl1_stderr = run_command_with_output(
            ["wsl", "--install", "-d", "Ubuntu", "--version", "1"], 
            logger, 
            timeout=900
        )
        
        # Wait a moment for WSL to process
        import time
        time.sleep(3)
        
        # Verify installation regardless of return code (Ubuntu may launch interactively)
        logger.log("", Colors.RESET)
        logger.log("🔍 Verifying Ubuntu installation...", Colors.BLUE)
        verify_rc, verify_out, verify_err = run_command_with_output(
            ["wsl", "--list", "--verbose"],
            logger,
            timeout=10,
            description="Checking installed WSL distributions"
        )
        
        ubuntu_installed = False
        ubuntu_distro = None
        if verify_rc == 0 and verify_out:
            output_lower = verify_out.lower()
            if "ubuntu" in output_lower and "no installed distributions" not in output_lower:
                ubuntu_installed = True
                ubuntu_distro = get_ubuntu_distro_name(logger, verify_out)
                if not ubuntu_distro:
                    ubuntu_distro = "Ubuntu"
        
        if ubuntu_installed or wsl1_rc == 0 or "already exists" in (wsl1_stdout + wsl1_stderr).lower():
            logger.log("✅ Ubuntu successfully installed using WSL1 fallback!", Colors.GREEN)
            if ubuntu_distro:
                logger.log(f"   Distribution: {ubuntu_distro}", Colors.CYAN)
            return True
        else:
            logger.log("⚠️ WSL1 installation completed but verification pending", Colors.YELLOW)
            logger.log("   Ubuntu may launch automatically. Please complete the setup.", Colors.CYAN)
            return False
            
    elif "already exists" in error_out or "distribution successfully installed" in error_out:
        # Wait a moment for WSL to process
        import time
        time.sleep(3)
        
        # Verify installation
        logger.log("", Colors.RESET)
        logger.log("🔍 Verifying Ubuntu installation...", Colors.BLUE)
        verify_rc, verify_out, verify_err = run_command_with_output(
            ["wsl", "--list", "--verbose"],
            logger,
            timeout=10,
            description="Checking installed WSL distributions"
        )
        
        if verify_rc == 0 and verify_out:
            output_lower = verify_out.lower()
            if "ubuntu" in output_lower and "no installed distributions" not in output_lower:
                ubuntu_distro = get_ubuntu_distro_name(logger, verify_out)
                if ubuntu_distro:
                    logger.log(f"✅ Ubuntu is already installed: {ubuntu_distro}", Colors.GREEN)
                    return True
        
        logger.log("✅ Ubuntu is already installed.", Colors.GREEN)
        return True
        
    # If we get here, check if Ubuntu was installed despite return code
    import time
    time.sleep(3)
    
    verify_rc, verify_out, verify_err = run_command_with_output(
        ["wsl", "--list", "--verbose"],
        logger,
        timeout=10,
        description="Checking installed WSL distributions"
    )
    
    if verify_rc == 0 and verify_out:
        output_lower = verify_out.lower()
        if "ubuntu" in output_lower and "no installed distributions" not in output_lower:
            ubuntu_distro = get_ubuntu_distro_name(logger, verify_out)
            if ubuntu_distro:
                logger.log(f"✅ Ubuntu installed successfully: {ubuntu_distro}", Colors.GREEN)
                logger.log("   (Installation command may have launched Ubuntu interactively)", Colors.CYAN)
                return True
    
    return rc == 0

def install_wsl2(logger):
    """Install WSL2 and Ubuntu on Windows."""
    logger.log("", Colors.RESET)
    logger.log("=" * 60, Colors.BLUE)
    logger.log("🔧 Installing WSL2 and Ubuntu", Colors.BLUE)
    logger.log("=" * 60, Colors.BLUE)
    logger.log("", Colors.RESET)
    
    # Check if running as administrator
    is_admin = check_admin_privileges()
    if not is_admin:
        logger.log("⚠️ Administrator privileges not detected.", Colors.YELLOW)
        logger.log("", Colors.RESET)
        logger.log("📋 For best results, run this script as Administrator:", Colors.CYAN)
        logger.log("   1. Right-click PowerShell or Command Prompt", Colors.YELLOW)
        logger.log("   2. Select 'Run as Administrator'", Colors.YELLOW)
        logger.log("   3. Navigate to this directory and run: python3 presetup.py", Colors.YELLOW)
        logger.log("", Colors.RESET)
        logger.log("   Continuing anyway... (may fail without admin privileges)", Colors.CYAN)
    logger.log("", Colors.RESET)
    
    logger.log("📥 This will install WSL2 and Ubuntu. This may take 5-10 minutes.", Colors.YELLOW)
    logger.log("   DISM commands can take 2-5 minutes each - please be patient.", Colors.CYAN)
    logger.log("", Colors.RESET)
    
    installation_success = False
    step_results = []  # Track step results: [(step_name, status, message)]
    
    try:
        # Step 1: Enable WSL feature
        logger.log("Step 1/3: Enabling WSL feature...", Colors.BLUE)
        logger.log("   This may take 2-5 minutes. Please wait...", Colors.CYAN)
        try:
            returncode, stdout, stderr = run_command_with_output(
                ["dism.exe", "/online", "/enable-feature", "/featurename:Microsoft-Windows-Subsystem-Linux", "/all", "/norestart"],
                logger,
                timeout=300,
                description="Enabling WSL feature via DISM"
            )
            if returncode == 0:
                logger.log("✅ WSL feature enabled", Colors.GREEN)
                step_results.append(("Step 1: Enable WSL feature", "PASSED", "WSL feature enabled successfully"))
            else:
                error_output = stderr if stderr else stdout
                if "access is denied" in error_output.lower() or "administrator" in error_output.lower():
                    logger.log("⚠️ WSL feature requires Administrator privileges", Colors.YELLOW)
                    logger.log("   Please run this script as Administrator", Colors.CYAN)
                    step_results.append(("Step 1: Enable WSL feature", "FAILED", "Requires Administrator privileges"))
                else:
                    logger.log("⚠️ WSL feature may already be enabled", Colors.YELLOW)
                    step_results.append(("Step 1: Enable WSL feature", "WARNING", "May already be enabled"))
        except subprocess.TimeoutExpired:
            logger.log("⏱️ WSL feature enable timed out (took longer than 5 minutes)", Colors.YELLOW)
            logger.log("   This usually means:", Colors.CYAN)
            logger.log("   • The operation is still running in the background", Colors.YELLOW)
            logger.log("   • You need Administrator privileges", Colors.YELLOW)
            logger.log("   • A restart may be required", Colors.YELLOW)
            logger.log("", Colors.RESET)
            logger.log("💡 Try running PowerShell as Administrator and run:", Colors.CYAN)
            logger.log("   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all", Colors.YELLOW)
            step_results.append(("Step 1: Enable WSL feature", "FAILED", "Command timed out"))
        except Exception as e:
            logger.log(f"⚠️ Could not enable WSL feature: {e}", Colors.YELLOW)
            logger.log("   You may need to run this script as Administrator", Colors.CYAN)
            step_results.append(("Step 1: Enable WSL feature", "FAILED", f"Error: {e}"))
        
        # Step 2: Enable Virtual Machine Platform
        logger.log("", Colors.RESET)
        logger.log("Step 2/3: Enabling Virtual Machine Platform...", Colors.BLUE)
        logger.log("   This may take 2-5 minutes. Please wait...", Colors.CYAN)
        try:
            returncode, stdout, stderr = run_command_with_output(
                ["dism.exe", "/online", "/enable-feature", "/featurename:VirtualMachinePlatform", "/all", "/norestart"],
                logger,
                timeout=300,
                description="Enabling Virtual Machine Platform via DISM"
            )
            if returncode == 0:
                logger.log("✅ Virtual Machine Platform enabled", Colors.GREEN)
                logger.log("", Colors.RESET)
                logger.log("⚠️ IMPORTANT: Virtual Machine Platform requires a restart to activate", Colors.YELLOW)
                logger.log("   If Ubuntu installation fails, restart your computer and run this script again", Colors.CYAN)
                step_results.append(("Step 2: Enable Virtual Machine Platform", "PASSED", "Enabled (restart required to activate)"))
            else:
                error_output = stderr if stderr else stdout
                if "access is denied" in error_output.lower() or "administrator" in error_output.lower():
                    logger.log("⚠️ Virtual Machine Platform requires Administrator privileges", Colors.YELLOW)
                    logger.log("   Please run this script as Administrator", Colors.CYAN)
                    step_results.append(("Step 2: Enable Virtual Machine Platform", "FAILED", "Requires Administrator privileges"))
                else:
                    logger.log("⚠️ Virtual Machine Platform may already be enabled", Colors.YELLOW)
                    step_results.append(("Step 2: Enable Virtual Machine Platform", "WARNING", "May already be enabled"))
        except subprocess.TimeoutExpired:
            logger.log("⏱️ Virtual Machine Platform enable timed out (took longer than 5 minutes)", Colors.YELLOW)
            logger.log("   This usually means:", Colors.CYAN)
            logger.log("   • The operation is still running in the background", Colors.YELLOW)
            logger.log("   • You need Administrator privileges", Colors.YELLOW)
            logger.log("   • A restart may be required", Colors.YELLOW)
            logger.log("", Colors.RESET)
            logger.log("💡 Try running PowerShell as Administrator and run:", Colors.CYAN)
            logger.log("   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all", Colors.YELLOW)
            step_results.append(("Step 2: Enable Virtual Machine Platform", "FAILED", "Command timed out"))
        except Exception as e:
            logger.log(f"⚠️ Could not enable Virtual Machine Platform: {e}", Colors.YELLOW)
            step_results.append(("Step 2: Enable Virtual Machine Platform", "FAILED", f"Error: {e}"))
        
        # Step 3: Set WSL2 as default
        logger.log("", Colors.RESET)
        logger.log("Step 3/3: Setting WSL2 as default version...", Colors.BLUE)
        try:
            returncode, stdout, stderr = run_command_with_output(
                ["wsl", "--set-default-version", "2"],
                logger,
                timeout=60,
                description="Setting WSL2 as default version"
            )
            if returncode == 0:
                logger.log("✅ WSL2 set as default version", Colors.GREEN)
                step_results.append(("Step 3: Set WSL2 as default version", "PASSED", "WSL2 set as default"))
            else:
                error_output = stderr if stderr else stdout
                if "restart" in error_output.lower():
                    logger.log("⚠️ A restart is required before setting WSL2 as default", Colors.YELLOW)
                    step_results.append(("Step 3: Set WSL2 as default version", "FAILED", "Restart required"))
                else:
                    logger.log("⚠️ Could not set WSL2 as default (may need restart)", Colors.YELLOW)
                    step_results.append(("Step 3: Set WSL2 as default version", "WARNING", "May need restart"))
        except subprocess.TimeoutExpired:
            logger.log("⏱️ Setting WSL2 default version timed out", Colors.YELLOW)
            logger.log("   This may require a restart first", Colors.CYAN)
            step_results.append(("Step 3: Set WSL2 as default version", "FAILED", "Command timed out"))
        except Exception as e:
            logger.log(f"⚠️ Could not set WSL2 as default: {e}", Colors.YELLOW)
            step_results.append(("Step 3: Set WSL2 as default version", "FAILED", f"Error: {e}"))
        
        # Step 4: Install Ubuntu automatically with user setup
        logger.log("", Colors.RESET)
        logger.log("Step 4/4: Installing Ubuntu...", Colors.BLUE)
        logger.log("", Colors.RESET)
        
        # Check if already installed to avoid unnecessary steps
        rc, list_out = run_cmd(["wsl", "--list", "--verbose"], logger)
        if "ubuntu" in list_out.lower() and "no installed distributions" not in list_out.lower():
            logger.log("✅ Ubuntu detected.", Colors.GREEN)
            installation_success = True
        else:
            # Prompt user early so the rest of the process is hands-off
            logger.log("", Colors.RESET)
            logger.log("--- Linux Account Setup ---", Colors.CYAN)
            logger.log("", Colors.RESET)
            new_user = input("Enter desired Ubuntu username: ").strip().lower()
            new_pass = input("Enter desired Ubuntu password: ").strip()
            
            # Attempt standard WSL2 installation
            logger.log("", Colors.RESET)
            logger.log("🚀 Attempting WSL2 installation...", Colors.CYAN)
            rc, out = run_cmd(["wsl", "--install", "-d", "Ubuntu", "--no-launch"], logger)
            
            # Pivot to WSL1 if UTM blocks nested virtualization
            if "hcs_e_hyperv_not_installed" in out or "wsl2 is not supported" in out.lower():
                logger.log("", Colors.RESET)
                logger.log("⚠️  WSL2 blocked by UTM settings. Switching to WSL1 Fallback...", Colors.YELLOW)
                run_cmd(["wsl", "--set-default-version", "1"], logger)
                rc, out = run_cmd(["wsl", "--install", "-d", "Ubuntu", "--version", "1", "--no-launch"], logger)
            
            if "already exists" in out.lower() or rc == 0:
                logger.log("📦 Distribution files ready.", Colors.GREEN)
                
                # Pause to let the filesystem initialize
                import time
                time.sleep(3)
                
                try:
                    setup_wsl_user(logger, new_user, new_pass)
                    logger.log("✅ User creation successful.", Colors.GREEN)
                    installation_success = True
                except Exception as e:
                    logger.log(f"⚠️ User injection failed: {e}", Colors.YELLOW)
                    installation_success = False
            else:
                logger.log(f"❌ Failed to install: {out}", Colors.RED)
                installation_success = False
            
    except Exception as e:
        logger.log(f"❌ Failed to install WSL2: {e}", Colors.RED)
        logger.log("", Colors.RESET)
    
    # Display summary of steps
    logger.log("", Colors.RESET)
    logger.log("", Colors.RESET)
    logger.log("=" * 70, Colors.BLUE)
    logger.log("📊 Installation Summary", Colors.BLUE)
    logger.log("=" * 70, Colors.BLUE)
    logger.log("", Colors.RESET)
    
    passed_steps = [s for s in step_results if s[1] == "PASSED"]
    failed_steps = [s for s in step_results if s[1] == "FAILED"]
    warning_steps = [s for s in step_results if s[1] == "WARNING"]
    
    if passed_steps:
        logger.log("✅ Steps Completed Successfully:", Colors.GREEN)
        for step_name, status, message in passed_steps:
            logger.log(f"   ✓ {step_name}", Colors.GREEN)
            if message:
                logger.log(f"     → {message}", Colors.CYAN)
        logger.log("", Colors.RESET)
    
    if warning_steps:
        logger.log("⚠️ Steps with Warnings:", Colors.YELLOW)
        for step_name, status, message in warning_steps:
            logger.log(f"   ⚠ {step_name}", Colors.YELLOW)
            if message:
                logger.log(f"     → {message}", Colors.CYAN)
        logger.log("", Colors.RESET)
    
    if failed_steps:
        logger.log("❌ Steps Failed:", Colors.RED)
        for step_name, status, message in failed_steps:
            logger.log(f"   ✗ {step_name}", Colors.RED)
            if message:
                logger.log(f"     → {message}", Colors.YELLOW)
        logger.log("", Colors.RESET)
    
    logger.log("=" * 70, Colors.BLUE)
    logger.log("", Colors.RESET)
    
    # Show next steps based on installation result
    if installation_success:
        logger.log("", Colors.RESET)
        logger.log("=" * 50, Colors.GREEN)
        logger.log("🎉 PRE-SETUP COMPLETE - ENTERING LINUX", Colors.GREEN)
        logger.log("=" * 50, Colors.GREEN)
        logger.log("", Colors.RESET)
        
        logger.log("✅ Ubuntu installation complete!", Colors.GREEN)
        logger.log("", Colors.RESET)
        logger.log("📋 Next Steps:", Colors.CYAN)
        logger.log("", Colors.RESET)
        logger.log("   1. Open a new terminal/PowerShell window", Colors.YELLOW)
        logger.log("   2. Run: wsl -d Ubuntu", Colors.YELLOW)
        logger.log("   3. Navigate to your project: cd Downloads/customnerd-main/customnerd-main/", Colors.YELLOW)
        logger.log("      (Path may vary depending on where you downloaded the project)", Colors.CYAN)
        logger.log("   4. Run: python3 setup.py", Colors.YELLOW)
        logger.log("", Colors.RESET)
        
        return True
    else:
        display_manual_instructions(
            logger,
            "📋 TROUBLESHOOTING & NEXT STEPS",
            [
                {
                    'title': 'Check if a restart is needed',
                    'notes': [
                        'If Windows prompted for a restart, restart now',
                        'After restart, run this script again'
                    ]
                },
                {
                    'title': 'If you got "access denied" or timeout errors',
                    'notes': [
                        'Right-click PowerShell',
                        'Select "Run as Administrator"',
                        'Navigate to this directory',
                        'Run: python3 presetup.py'
                    ]
                },
                {
                    'title': 'Manual installation (if automatic failed)',
                    'commands': [
                        'wsl --install -d Ubuntu'
                    ],
                    'notes': [
                        'Open PowerShell as Administrator',
                        'Restart when prompted',
                        'After restart, Ubuntu will launch automatically',
                        'Set up your Ubuntu username and password',
                        'Run this script again'
                    ]
                }
            ]
        )
    
        return False

def prompt_ubuntu_setup(logger, distro="Ubuntu"):
    """Prompt user to complete Ubuntu initial setup."""
    # Get the exact distribution name if not provided
    if not distro or distro == "Ubuntu":
        distro = get_ubuntu_distro_name(logger) or "Ubuntu"
    
    logger.log("", Colors.RESET)
    logger.log("=" * 60, Colors.BLUE)
    logger.log("📋 Ubuntu Initial Setup Required", Colors.BLUE)
    logger.log("=" * 60, Colors.BLUE)
    logger.log("", Colors.RESET)
    logger.log(f"Ubuntu ({distro}) is installed but needs initial user configuration.", Colors.YELLOW)
    logger.log("", Colors.RESET)
    logger.log("Please follow these steps:", Colors.CYAN)
    logger.log("", Colors.RESET)
    logger.log("1️⃣  Launch Ubuntu:", Colors.BLUE)
    logger.log("   • From Start Menu: Search for 'Ubuntu' and click it", Colors.YELLOW)
    logger.log(f"   • Or run in PowerShell: wsl -d {distro}", Colors.YELLOW)
    logger.log("", Colors.RESET)
    logger.log("2️⃣  Create your Ubuntu user account:", Colors.BLUE)
    logger.log("   • Enter your desired username (lowercase, no spaces)", Colors.YELLOW)
    logger.log("   • Enter and confirm your password", Colors.YELLOW)
    logger.log("   • Wait for Ubuntu to finish initializing", Colors.YELLOW)
    logger.log("", Colors.RESET)
    logger.log("3️⃣  Verify setup:", Colors.BLUE)
    logger.log("   • You should see a command prompt like: username@computername:~$", Colors.YELLOW)
    logger.log("   • Type 'exit' to close Ubuntu", Colors.YELLOW)
    logger.log("", Colors.RESET)
    logger.log("4️⃣  Run this script again:", Colors.BLUE)
    logger.log("   python3 presetup.py", Colors.YELLOW)
    logger.log("", Colors.RESET)
    logger.log("=" * 60, Colors.BLUE)
    logger.log("", Colors.RESET)
    
    response = input("Have you completed the Ubuntu setup? (y/n): ").strip().lower()
    if response == 'y' or response == 'yes':
        # Check again using the exact distribution name
        if check_ubuntu_setup_complete(logger, distro):
            return True
        else:
            logger.log("⚠️ Ubuntu setup still not complete. Please follow the steps above.", Colors.YELLOW)
            return False
    else:
        logger.log("", Colors.RESET)
        logger.log("Please complete the Ubuntu setup and run this script again.", Colors.CYAN)
        return False

def verify_ubuntu_ready(logger, distro="Ubuntu"):
    """Verify Ubuntu is fully ready and can run commands."""
    logger.log("", Colors.RESET)
    logger.log("🔍 Verifying Ubuntu is ready...", Colors.BLUE)
    
    # Check if we can run basic commands
    try:
        # Test whoami
        result = subprocess.run(
            ["wsl", "-d", distro, "whoami"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            username = result.stdout.strip()
            logger.log(f"✅ Ubuntu user: {username}", Colors.GREEN)
        else:
            logger.log("❌ Cannot verify Ubuntu user", Colors.RED)
            return False
        
        # Test basic command
        result = subprocess.run(
            ["wsl", "-d", distro, "echo", "test"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.log("✅ Ubuntu is responding to commands", Colors.GREEN)
        else:
            logger.log("⚠️ Ubuntu may not be fully ready", Colors.YELLOW)
            return False
        
        # Check if Python3 is available (or can be installed)
        result = subprocess.run(
            ["wsl", "-d", distro, "which", "python3"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.log("✅ Python3 is available in Ubuntu", Colors.GREEN)
        else:
            logger.log("⚠️ Python3 not found (will be installed during setup.py)", Colors.YELLOW)
        
        return True
    except Exception as e:
        logger.log(f"❌ Error verifying Ubuntu: {e}", Colors.RED)
        return False

def main():
    # Check if running on Windows
    if platform.system() != "Windows":
        print("=" * 60)
        print("❌ This script is for Windows only!")
        print("=" * 60)
        print("")
        print("If you're on macOS or Linux, you can run setup.py directly.")
        print("If you're on Windows, please run this script from Windows (not WSL).")
        sys.exit(1)
    
    # Check if already running inside WSL
    if os.environ.get('WSL_DISTRO_NAME'):
        print("=" * 60)
        print("⚠️  You're running this script inside WSL!")
        print("=" * 60)
        print("")
        print("This script should be run from Windows PowerShell or Command Prompt,")
        print("not from inside WSL.")
        print("")
        print("Please:")
        print("1. Exit WSL (type 'exit')")
        print("2. Open PowerShell or Command Prompt")
        print("3. Run: python3 presetup.py")
        sys.exit(1)
    
    base_dir = Path(__file__).parent.absolute()
    logs_dir = base_dir / "logs" / "presetup"
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    day = now.strftime("%d")
    mon = now.strftime("%b")
    year = now.strftime("%Y")
    hour = now.strftime("%I").lstrip("0") or "0"
    minute = now.strftime("%M")
    ampm = now.strftime("%p").lower()
    ts = f"{day}_{mon}_{year}_{hour}_{minute}_{ampm}"
    log_file_path = logs_dir / f"presetup_{ts}.log"
    logger = Logger(log_file_path)
    
    try:
        logger.log("", Colors.RESET)
        logger.log("=" * 60, Colors.BLUE)
        logger.log("🪟 Custom-Nerd/Nerd-Engine Windows WSL2 Setup Wizard", Colors.BLUE)
        logger.log("=" * 60, Colors.BLUE)
        logger.log("", Colors.RESET)
        logger.log("This script will set up WSL2 and Ubuntu for Windows.", Colors.CYAN)
        logger.log("After this completes, activate WSL and run 'sudo python3 setup.py' to continue.", Colors.CYAN)
        logger.log("", Colors.RESET)
        logger.log(f"📝 Logging to: {log_file_path}", Colors.YELLOW)
        logger.log("", Colors.RESET)

        # Check current WSL status
        logger.log("🔍 Checking WSL2 status...", Colors.BLUE)
        wsl_installed, distro, ready = check_wsl_installed(logger)
        
        # Check for catastrophic failure if Ubuntu is detected
        if wsl_installed and distro and "ubuntu" in distro.lower():
            if check_wsl_catastrophic_failure(logger, distro):
                logger.log("", Colors.RESET)
                logger.log("❌ WSL is experiencing a catastrophic failure error.", Colors.RED)
                logger.log("", Colors.RESET)
                logger.log("📋 This usually means Ubuntu needs to be unregistered and reinstalled.", Colors.CYAN)
                logger.log("", Colors.RESET)
                logger.log("Would you like to automatically fix this? (y/n): ", Colors.YELLOW)
                response = input().strip().lower()
                if response == 'y' or response == 'yes':
                    logger.log("", Colors.RESET)
                    logger.log("🔧 Attempting to fix WSL...", Colors.BLUE)
                    logger.log("", Colors.RESET)
                    logger.log(f"Step 1/2: Unregistering Ubuntu ({distro})...", Colors.CYAN)
                    try:
                        unregister_returncode, unregister_stdout, unregister_stderr = run_command_with_output(
                            ["wsl", "--unregister", distro],
                            logger,
                            timeout=30,
                            description="Unregistering Ubuntu distribution"
                        )
                        if unregister_returncode == 0:
                            logger.log("✅ Ubuntu unregistered successfully", Colors.GREEN)
                        else:
                            logger.log("⚠️ Unregister command completed with warnings", Colors.YELLOW)
                    except Exception as e:
                        logger.log(f"⚠️ Could not unregister Ubuntu: {e}", Colors.YELLOW)
                        logger.log(f"   Please run manually: wsl --unregister {distro}", Colors.CYAN)
                    
                    logger.log("", Colors.RESET)
                    logger.log("Step 2/2: Reinstalling Ubuntu...", Colors.CYAN)
                    logger.log("   This will download Ubuntu (~200MB) and may take several minutes.", Colors.YELLOW)
                    try:
                        install_returncode, install_stdout, install_stderr = run_command_with_output(
                            ["wsl", "--install", "-d", "Ubuntu"],
                            logger,
                            timeout=600,
                            description="Reinstalling Ubuntu distribution"
                        )
                        if install_returncode == 0:
                            logger.log("✅ Ubuntu reinstalled successfully!", Colors.GREEN)
                            logger.log("", Colors.RESET)
                            logger.log("⚠️ IMPORTANT: Ubuntu will launch automatically.", Colors.YELLOW)
                            logger.log("   Please complete the initial setup (username and password).", Colors.CYAN)
                            logger.log("   Then run this script again to verify everything is ready.", Colors.CYAN)
                            logger.log("", Colors.RESET)
                            return
                        else:
                            logger.log("⚠️ Installation may require a restart or manual steps", Colors.YELLOW)
                            logger.log("   Please check the [Internal Check] output above for details.", Colors.CYAN)
                    except Exception as e:
                        logger.log(f"❌ Could not reinstall Ubuntu: {e}", Colors.RED)
                        logger.log("   Please run manually: wsl --install -d Ubuntu", Colors.CYAN)
                else:
                    display_manual_instructions(
                        logger,
                        "📋 MANUAL FIX STEPS",
                        [
                            {
                                'title': f'Unregister corrupted Ubuntu',
                                'commands': [f'wsl --unregister {distro}']
                            },
                            {
                                'title': 'Reinstall Ubuntu',
                                'commands': ['wsl --install -d Ubuntu']
                            },
                            {
                                'title': 'Complete Ubuntu setup',
                                'notes': [
                                    'After Ubuntu launches, create your username and password'
                                ]
                            },
                            {
                                'title': 'Run this script again',
                                'commands': ['python3 presetup.py']
                            }
                        ]
                    )
                    sys.exit(1)
        
        if ready and distro and "ubuntu" in distro.lower():
            logger.log("", Colors.RESET)
            logger.log("✅ WSL2 and Ubuntu are already set up and ready!", Colors.GREEN)
            logger.log("", Colors.RESET)
            
            # Verify it's actually ready
            if verify_ubuntu_ready(logger, distro):
                logger.log("", Colors.RESET)
                logger.log("=" * 50, Colors.GREEN)
                logger.log("🎉 PRE-SETUP COMPLETE", Colors.GREEN)
                logger.log("=" * 50, Colors.GREEN)
                logger.log("", Colors.RESET)
                
                logger.log("✅ WSL2 and Ubuntu are ready!", Colors.GREEN)
                logger.log("", Colors.RESET)
                logger.log("📋 Next Steps:", Colors.CYAN)
                logger.log("", Colors.RESET)
                logger.log(f"   1. Open a new terminal/PowerShell window", Colors.YELLOW)
                logger.log(f"   2. Run: wsl -d {distro}", Colors.YELLOW)
                logger.log(f"   3. Navigate to your project: cd Downloads/customnerd-main/customnerd-main/", Colors.YELLOW)
                logger.log("      (Path may vary depending on where you downloaded the project)", Colors.CYAN)
                logger.log(f"   4. Run: python3 setup.py", Colors.YELLOW)
                logger.log("", Colors.RESET)
                return
            else:
                logger.log("", Colors.RESET)
                logger.log("⚠️ Ubuntu is installed but not fully ready.", Colors.YELLOW)
                logger.log("   Attempting to fix...", Colors.CYAN)
        
        elif wsl_installed and distro and "ubuntu" in distro.lower() and not ready:
            logger.log("", Colors.RESET)
            logger.log("⚠️ Ubuntu is installed but needs initial user setup.", Colors.YELLOW)
            logger.log("", Colors.RESET)
            
            if prompt_ubuntu_setup(logger, distro):
                if verify_ubuntu_ready(logger, distro):
                    logger.log("", Colors.RESET)
                    logger.log("=" * 50, Colors.GREEN)
                    logger.log("🎉 PRE-SETUP COMPLETE", Colors.GREEN)
                    logger.log("=" * 50, Colors.GREEN)
                    logger.log("", Colors.RESET)
                    
                    logger.log("✅ WSL2 and Ubuntu are ready!", Colors.GREEN)
                    logger.log("", Colors.RESET)
                    logger.log("📋 Next Steps:", Colors.CYAN)
                    logger.log("", Colors.RESET)
                    logger.log(f"   1. Open a new terminal/PowerShell window", Colors.YELLOW)
                    logger.log(f"   2. Run: wsl -d {distro}", Colors.YELLOW)
                    logger.log(f"   3. Navigate to your project: cd Downloads/customnerd-main/customnerd-main/", Colors.YELLOW)
                    logger.log("      (Path may vary depending on where you downloaded the project)", Colors.CYAN)
                    logger.log(f"   4. Run: python3 setup.py", Colors.YELLOW)
                    logger.log("", Colors.RESET)
                    return
            else:
                logger.log("", Colors.RESET)
                logger.log("❌ Ubuntu setup is not complete. Please follow the instructions above.", Colors.RED)
                sys.exit(1)
        
        elif wsl_installed and not distro:
            logger.log("", Colors.RESET)
            logger.log("⚠️ WSL is installed but Ubuntu is not found.", Colors.YELLOW)
            logger.log("   Installing Ubuntu...", Colors.CYAN)
            logger.log("", Colors.RESET)
            
            if install_wsl2(logger):
                logger.log("", Colors.RESET)
                logger.log("⚠️ Installation initiated. A restart may be required.", Colors.YELLOW)
                logger.log("   After restart, run this script again to complete setup.", Colors.CYAN)
                sys.exit(0)
            else:
                logger.log("", Colors.RESET)
                logger.log("❌ Failed to install Ubuntu. Please check the errors above.", Colors.RED)
                sys.exit(1)
        
        else:
            logger.log("", Colors.RESET)
            logger.log("❌ WSL2 is not installed.", Colors.RED)
            logger.log("", Colors.RESET)
            
            response = input("Would you like to install WSL2 and Ubuntu now? (y/n): ").strip().lower()
            if response == 'y' or response == 'yes':
                if install_wsl2(logger):
                    logger.log("", Colors.RESET)
                    logger.log("⚠️ Installation initiated. A restart may be required.", Colors.YELLOW)
                    logger.log("   After restart, run this script again to complete setup.", Colors.CYAN)
                    sys.exit(0)
                else:
                    logger.log("", Colors.RESET)
                    logger.log("❌ Installation failed. Please check the errors above.", Colors.RED)
                    logger.log("   You may need to run this script as Administrator.", Colors.YELLOW)
                    sys.exit(1)
            else:
                logger.log("", Colors.RESET)
                logger.log("Setup cancelled. WSL2 is required for Windows users.", Colors.YELLOW)
                sys.exit(0)
        
    except KeyboardInterrupt:
        logger.log("", Colors.RESET)
        logger.log("Setup cancelled by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        logger.log(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    finally:
        logger.close()

if __name__ == "__main__":
    main()

