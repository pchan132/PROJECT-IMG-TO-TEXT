from typing import Iterable


def flatten_box(box: Iterable[Iterable[float]]) -> list[int]:
    return [int(v) for point in box for v in point]


def bounds(box: Iterable[Iterable[float]]) -> tuple[int, int, int, int]:
    points = list(box)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
