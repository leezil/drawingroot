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


def segment_distance(point, start, end):
    """점에서 선분까지의 최단 평면 거리. 선분 바깥에서는 끝점을 사용한다."""
    segment_length = distance(start, end)
    if segment_length == 0.0:
        return distance(point, start)
    if not math.isfinite(segment_length):
        raise ValueError("선분이 계산 가능한 범위를 넘었습니다.")

    direction_x = (end[0] - start[0]) / segment_length
    direction_y = (end[1] - start[1]) / segment_length
    along = ((point[0] - start[0]) * direction_x
             + (point[1] - start[1]) * direction_y)
    if not math.isfinite(along):
        raise ValueError("점의 위치가 계산 가능한 범위를 넘었습니다.")

    if along <= 0.0:
        closest = start
    elif along >= segment_length:
        closest = end
    else:
        closest = (start[0] + direction_x * along,
                   start[1] + direction_y * along)
    return distance(point, closest)
