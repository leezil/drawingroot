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


def polyline_distance(point, points):
    """점에서 입력 순서대로 이은 선 전체까지의 최단거리. 자동으로 닫지 않는다."""
    if len(points) == 0:
        raise ValueError("비교할 선의 좌표가 하나 이상 필요합니다.")
    if len(points) == 1:
        return distance(point, points[0])

    closest_distance = math.inf
    for index in range(1, len(points)):
        gap = segment_distance(point, points[index - 1], points[index])
        closest_distance = min(closest_distance, gap)
    return closest_distance


def resample(points, count):
    """원본 선을 따라 같은 간격으로 count개의 새 점을 배치한다. 양 끝점을 포함한다."""
    if type(count) is not int or count < 2:
        raise ValueError("새 점 개수는 2 이상의 정수여야 합니다.")
    if len(points) == 0:
        raise ValueError("재배치할 선의 좌표가 하나 이상 필요합니다.")

    total = length(points)
    if not math.isfinite(total):
        raise ValueError("선의 길이가 계산 가능한 범위를 넘었습니다.")
    if total == 0.0:
        return [tuple(points[0]) for _ in range(count)]

    sampled = [tuple(points[0])]
    segment_index = 1
    walked = 0.0
    segment_length = distance(points[0], points[1])
    for sample_index in range(1, count - 1):
        target = total * (sample_index / (count - 1))
        while segment_index < len(points) - 1 and (
            segment_length == 0.0 or walked + segment_length < target
        ):
            walked += segment_length
            segment_index += 1
            segment_length = distance(points[segment_index - 1], points[segment_index])

        start, end = points[segment_index - 1], points[segment_index]
        ratio = 0.0 if segment_length == 0.0 else (target - walked) / segment_length
        ratio = max(0.0, min(1.0, ratio))
        sampled.append((start[0] + (end[0] - start[0]) * ratio,
                        start[1] + (end[1] - start[1]) * ratio))
    sampled.append(tuple(points[-1]))
    return sampled


def mean_distance(source, target, count=64):
    """source의 균등 샘플에서 target 원본 선까지 거리의 평균. 단방향 측정이다."""
    if len(target) == 0:
        raise ValueError("비교할 선의 좌표가 하나 이상 필요합니다.")
    samples = resample(source, count)
    gaps = [polyline_distance(point, target) for point in samples]
    if not all(math.isfinite(gap) for gap in gaps):
        raise ValueError("거리 계산이 가능한 범위를 넘었습니다.")
    # 합계가 넘치지 않도록 각각 나눈 뒤 정밀하게 더한다.
    return math.fsum(gap / len(samples) for gap in gaps)


def symmetric_mean_distance(a, b, count=64):
    """두 방향의 평균 거리를 같은 비중으로 합친다. 이동 순서는 평가하지 않는다."""
    forward = mean_distance(a, b, count)
    backward = mean_distance(b, a, count)
    return forward / 2 + backward / 2


def frechet(a, b):
    """두 점 목록의 진행 순서를 유지하는 이산 프레셰 거리. 자동 재배치는 하지 않는다."""
    if len(a) == 0 or len(b) == 0:
        raise ValueError("비교할 두 선에 좌표가 하나 이상 필요합니다.")

    previous = []
    for i, point_a in enumerate(a):
        row = []
        for j, point_b in enumerate(b):
            gap = distance(point_a, point_b)
            if math.isnan(gap):
                raise ValueError("거리 계산에 유효한 좌표가 필요합니다.")
            if i == 0 and j == 0:
                row.append(gap)
            elif i == 0:
                row.append(max(gap, row[j - 1]))
            elif j == 0:
                row.append(max(gap, previous[j]))
            else:
                best_previous = min(previous[j], previous[j - 1], row[j - 1])
                row.append(max(gap, best_previous))
        previous = row

    result = previous[-1]
    if not math.isfinite(result):
        raise ValueError("거리 계산이 가능한 범위를 넘었습니다.")
    return result
