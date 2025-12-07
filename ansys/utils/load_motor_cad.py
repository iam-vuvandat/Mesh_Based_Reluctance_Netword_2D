import ansys.motorcad.core as pymotorcad
import os
import warnings

def load_motor_cad(file_path):
    """
    Khởi động Motor-CAD và tải tệp .mot.
    Cảnh báo nếu tệp không ở ổ C:.
    (Phiên bản này giả định file_path LUÔN LUÔN là đường dẫn tuyệt đối)
    """
    
    # --- PHẦN CẢNH BÁO (Phiên bản rút gọn) ---
    try:
        # Giả định file_path đã tuyệt đối, tách ổ đĩa trực tiếp
        drive = os.path.splitdrive(file_path)[0]
        
        if drive.upper() != "C:":
            warnings.warn(
                f"Tệp đang được tải từ ổ đĩa [{drive}]. "
                "CẢNH BÁO: Chạy benchmark từ các ổ đĩa được đồng bộ hóa "
                "(như Google Drive, OneDrive...) có thể làm sai lệch kết quả hiệu suất.",
                UserWarning
            )
            
    except Exception as e:
        print(f"Không thể kiểm tra đường dẫn tệp: {e}")
    # --- KẾT THÚC PHẦN BỔ SUNG ---

    # Logic gốc
    mcad = pymotorcad.MotorCAD(keep_instance_open=True)
    mcad.load_from_file(file_path)
    return mcad