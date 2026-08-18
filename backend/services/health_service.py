def calculate_health_score(temperature, pressure, vibration):

    score = 100

    if temperature > 80:
        score -= 20

    if pressure > 100:
        score -= 20

    if vibration > 8:
        score -= 30

    return max(score, 0)