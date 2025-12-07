import numpy as np

def get_amplitude_error(data_true, data_pred):
    """
    Calculates the percentage amplitude error between two signals.

    Amplitude is defined as the peak absolute value (max(|Y|)) of the signal.
    The error is calculated as:
    Error (%) = |(amp_true - amp_pred)| / amp_true * 100

    Args:
        data_true (list or tuple): The reference data.
            Expected structure: [Y_data, ..., X_data] (Y at index 0, X at -1).
        data_pred (list or tuple): The predicted data to compare.
            Expected structure: [Y_data, ..., X_data] (Y at index 0, X at -1).

    Returns:
        float: The amplitude error as a percentage (%).
               Returns `np.inf` if the true amplitude is 0 but the
               predicted amplitude is not. Returns 0.0 if both are 0.
    """
    
    try:
        y_true = data_true[0]
        y_pred = data_pred[0]
        
        amp_true = np.max(np.abs(y_true))
        amp_pred = np.max(np.abs(y_pred))

        if amp_true == 0:
            return 0.0 if amp_pred == 0 else np.inf

        error = np.abs(amp_true - amp_pred)
        error_percent = (error / amp_true) * 100
        
        return error_percent

    except (IndexError, TypeError):
        print("Error: Invalid input data structure (missing [0] or invalid data).")
        return np.inf
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return np.inf