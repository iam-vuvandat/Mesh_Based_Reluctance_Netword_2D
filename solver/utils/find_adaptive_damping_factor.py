def find_adaptive_damping_factor(ref: float) -> float:
    """
    Tính damping factor tự thích ứng dựa trên các khoảng và giá trị cho trước.

    Returns
    -------
    float
        Damping factor trong khoảng [damping_min, damping_max].
    """

    
    thresholds = [0.00, 0.05, 0.10, 0.20, 0.99 ]
    values     = [0.10, 0.13, 0.15, 0.13 ]

    damping_min = values[0]
    damping_max = values[-1]

    if ref is None:
        return damping_max

    ref = abs(ref)

    damping_factor = values[-1]  
    for i in range(len(values)):
        if thresholds[i] <= ref < thresholds[i+1]:
            damping_factor = values[i]
            break

    return max(damping_min, min(damping_factor, damping_max))
