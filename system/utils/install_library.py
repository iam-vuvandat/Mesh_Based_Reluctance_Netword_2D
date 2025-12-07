import importlib
import subprocess
import sys

def install_library():
    
    PACKAGES_TO_INSTALL = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'shapely': 'shapely',
        'pympler': 'pympler',
        'scipy': 'scipy',
        'tqdm': 'tqdm',
        'imageio': 'imageio',
        
        # MAPPED PACKAGES (Module Name : PyPI Name)
        'win32com.client': 'pywin32',
        'ansys.motorcad.core': 'ansys-motorcad-core',
        # THÊM TÊN GÓI CHÍNH XÁC VÀO ĐÂY ĐỂ CÀI ĐẶT
        'sklearn': 'scikit-learn', 
        'pyamg':'pyamg'
    }

    installed = []

    for module_name, pypi_package_name in PACKAGES_TO_INSTALL.items():
        
        try:
            # Check for package existence using the module name
            importlib.import_module(module_name)
            installed.append(module_name)
            
        except ImportError:
            # Install the package using the correct PyPI name
            print(f"'{module_name}' not found. Installing '{pypi_package_name}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pypi_package_name])
                installed.append(module_name)
            
            except subprocess.CalledProcessError as e:
                # Log the error but continue to the next package
                print(f"WARNING: Installation of '{pypi_package_name}' FAILED with code {e.returncode}. Skipping.")
                continue
    
    return installed