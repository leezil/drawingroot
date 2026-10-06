"""그림과 경로를 다루기 위한 작은 평면 기하 함수."""

import math


def distance(a, b):
    """두 (x, y) 점의 평면 거리를 입력 좌표와 같은 단위로 반환한다."""
    delta_x = b[0] - a[0]
    delta_y = b[1] - a[1]
    return math.hypot(delta_x, delta_y)


def length(points):
    """점을 입력 순서대로 이은 선의 길이를 반환한다. 자동으로 닫지 않는다."""
    total = 0.0
    for index in range(1, len(points)):
        total += distance(points[index - 1], points[index])
    return total
