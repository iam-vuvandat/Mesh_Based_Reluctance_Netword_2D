import sys
import os
import matplotlib.pyplot as plt

def setup():

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)

    from system.utils.install_library import install_library

    install_library()

    # Cài đặt Combo chuẩn cho báo cáo khoa học:
    params = {
        'savefig.dpi': 600,             # Độ nét cao
        'savefig.bbox': 'tight'        # Cắt viền thừa  
    }

    # Cập nhật một lần
    plt.rcParams.update(params)
    return []
    def setup():

        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.append(project_root)

        from system.utils.install_library import install_library

        from system.core.bootstrap import enter_virtual_environment
        enter_virtual_environment()
        install_library()