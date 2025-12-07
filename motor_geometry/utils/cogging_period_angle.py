import math

def cogging_period_angle(Q, poles):
    """
    Tính góc cơ khí của 1 chu kỳ cogging torque (radian).

    Tham số:
        Q     : số rãnh stator
        poles : số cực rotor (2p)

    Trả về:
        góc cơ khí (radian) của 1 chu kỳ cogging torque
    """
    N_cogging = (Q * poles) // math.gcd(Q, poles)   # số chu kỳ cogging trong 1 vòng cơ khí
    angle_rad = 2 * math.pi / N_cogging             # radian cho 1 chu kỳ
    return angle_rad


