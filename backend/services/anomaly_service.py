def detect_anomaly(temperature):

    if temperature < 50:
        return "Normal"

    elif temperature < 100:
        return "Warning"

    else:
        return "Critical"