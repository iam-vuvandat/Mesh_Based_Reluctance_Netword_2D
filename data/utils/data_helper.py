import os, sys, pickle

def _get_data_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "core", "workspace.pkl")

def save(**kwargs):
    filepath = _get_data_path()
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            data = pickle.load(f)
    else:
        data = {}
    data.update(kwargs)
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

def load(*varnames):
    filepath = _get_data_path()
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    if len(varnames) == 1:
        return data[varnames[0]]
    elif varnames:
        return tuple(data[k] for k in varnames)
    return data

def clear():
    """
    Xóa toàn bộ dữ liệu trong file data.pkl.
    Nếu file tồn tại -> ghi lại dict rỗng.
    Nếu chưa có -> không làm gì.
    """
    filepath = _get_data_path()
    if os.path.exists(filepath):
        with open(filepath, "wb") as f:
            pickle.dump({}, f)