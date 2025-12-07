import os
import sys
import subprocess

# --- 1. CONFIGURATION ---
VENV_NAME = ".venv"

def find_project_root():
    """Locates the project root by assuming it is two levels up from this script."""
    path = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(path))
    return root

def is_activated_venv(root_path):
    """Checks if the current Python interpreter is the one inside the VENV."""
    return sys.prefix == os.path.join(root_path, VENV_NAME)

def enter_virtual_environment(main_script_name="main.py"):
    """
    Ensures the VENV is created, dependencies are installed, 
    and restarts the program using the VENV's Python interpreter if not already active.
    
    Returns True if execution can proceed (i.e., we are in the VENV).
    Returns False if an irrecoverable error occurs.
    """
    
    project_root = find_project_root()
    
    # Check if VENV is already active
    if is_activated_venv(project_root):
        # --- THAY ĐỔI: In thông báo ngắn gọn ---
        print("Entered virtual environment")
        return True 
    
    # --- VENV NOT ACTIVE: LAUNCH SETUP AND RESTART ---
    
    print("\n--- VENV CHECK: Running setup and attempting restart ---")

    # Define platform-specific setup script name and VENV Python executable path
    if sys.platform.startswith('win'):
        setup_script_name = "create_environment.bat"
        venv_python_executable = os.path.join(project_root, VENV_NAME, "Scripts", "python.exe")
    else: # macOS, Linux
        setup_script_name = "create_environment.sh"
        venv_python_executable = os.path.join(project_root, VENV_NAME, "bin", "python")

    # Path to the setup script (located next to this bootstrap file)
    setup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), setup_script_name)
    main_script_path = os.path.join(project_root, main_script_name)

    # 1. Run the setup script (to create venv and install dependencies)
    if os.path.exists(setup_script_path):
        print(f"Running setup script: {setup_script_name}...")
        try:
            # Use shell=True for .bat on Windows; it's fine for .sh too.
            subprocess.run([setup_script_path], shell=True, check=True, cwd=project_root)
            print("Setup script executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"FATAL ERROR: Setup script '{setup_script_name}' failed with code {e.returncode}.")
            input("Press Enter to exit...")
            return False
    else:
        print(f"WARNING: Setup script '{setup_script_name}' not found. Assuming VENV is already set up.")

    # 2. Restart the main program using the VENV's Python
    if os.path.exists(venv_python_executable):
        print(f"\n--- Restarting program using VENV Python ---")
        subprocess.run([venv_python_executable, main_script_path])
        sys.exit(0)
    else:
        print(f"FATAL ERROR: Could not find VENV Python executable at {venv_python_executable}.")
        print("Please check your setup script and VENV creation.")
        input("Press Enter to exit...")
        return False
        
    return True