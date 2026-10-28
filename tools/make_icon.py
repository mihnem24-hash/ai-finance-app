# -*- coding: utf-8 -*-
"""Генерация иконки приложения (assets/icon.png), без внешних зависимостей.

Использование:
    python -I tools/make_icon.py assets/icon.png

Рисуется 1024×1024 PNG: скруглённый градиентный «квадрат», столбцы
графика и «нейронный» узел — символ соединения финансов и AI.
"""

from __future__ import annotations

import math
import struct
import sys
import zlib

SIZE = 1024
GRADIENT_FROM = (0x3D, 0x5A, 0xFE)  # синий
GRADIENT_TO = (0x8E, 0x4B, 0xFF)    # фиолетовый
WHITE = (255, 255, 255)


def sdf_rounded_rect(x: float, y: float, cx: float, cy: float,
                     half_w: float, half_h: float, radius: float) -> float:
    qx = abs(x - cx) - (half_w - radius)
    qy = abs(y - cy) - (half_h - radius)
    return min(max(qx, qy), 0.0) + math.hypot(max(qx, 0.0), max(qy, 0.0)) - radius


def sdf_circle(x: float, y: float, cx: float, cy: float, radius: float) -> float:
    return math.hypot(x - cx, y - cy) - radius


def blend(pixel: bytearray, index: int, color: tuple[int, int, int], alpha: float) -> None:
    if alpha <= 0:
        return
    if alpha >= 1:
        pixel[index:index + 3] = bytes(color)
        pixel[index + 3] = 255
        return
    base = 1.0 - alpha
    for channel in range(3):
        pixel[index + channel] = int(pixel[index + channel] * base + color[channel] * alpha)
    pixel[index + 3] = max(pixel[index + 3], int(255 * alpha))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def render() -> bytearray:
    size = SIZE
    pixels = bytearray(size * size * 4)
    center = size / 2.0
    outer_r = size * 0.225
    half = size / 2.0 - size * 0.045

    for y in range(size):
        row = y * size * 4
        for x in range(size):
            px = x + 0.5
            py = y + 0.5

            sdf = sdf_rounded_rect(px, py, center, center, half, half, outer_r)
            if sdf > 1.0:
                continue
            alpha = min(1.0, max(0.0, 0.5 - sdf))

            t = (px + py) / (2.0 * size)
            color = (
                int(lerp(GRADIENT_FROM[0], GRADIENT_TO[0], t)),
                int(lerp(GRADIENT_FROM[1], GRADIENT_TO[1], t)),
                int(lerp(GRADIENT_FROM[2], GRADIENT_TO[2], t)),
            )
            blend(pixels, row + x * 4, color, alpha)

    # Столбики диаграммы (скруглённые прямоугольники).
    bar_width = size * 0.085
    bar_gap = size * 0.055
    base_y = size * 0.76
    heights = [size * 0.16, size * 0.245, size * 0.33]
    start_x = size * 0.20
    for i, height in enumerate(heights):
        cx = start_x + i * (bar_width + bar_gap) + bar_width / 2.0
        cy = base_y - height / 2.0
        radius = bar_width / 2.0
        x0 = int(cx - bar_width / 2.0) - 2
        x1 = int(cx + bar_width / 2.0) + 2
        y0 = int(cy - height / 2.0) - 2
        y1 = int(cy + height / 2.0) + 2
        for y in range(max(0, y0), min(size, y1)):
            row = y * size * 4
            for x in range(max(0, x0), min(size, x1)):
                sdf = sdf_rounded_rect(x + 0.5, y + 0.5, cx, cy, bar_width / 2.0, height / 2.0, radius)
                blend(pixels, row + x * 4, WHITE, min(1.0, max(0.0, 0.5 - sdf)) * 0.92)

    # «Нейронный узел»: кольцо и три точки, соединённые линиями.
    ring_cx, ring_cy, ring_r = size * 0.705, size * 0.315, size * 0.135
    thickness = size * 0.022
    nodes = [
        (ring_cx, ring_cy - ring_r * 0.72),
        (ring_cx - ring_r * 0.82, ring_cy + ring_r * 0.55),
        (ring_cx + ring_r * 0.82, ring_cy + ring_r * 0.55),
    ]

    def draw_segment(x: int, y: int) -> float:
        px, py = x + 0.5, y + 0.5
        best = float("inf")
        for a in nodes:
            ax, ay = a
            for b in nodes:
                bx, by = b
                if a >= b:
                    continue
                dx, dy = bx - ax, by - ay
                length_sq = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
                best = min(best, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
        return best - thickness / 2.0

    x0 = int(ring_cx - ring_r) - 4
    x1 = int(ring_cx + ring_r) + 4
    y0 = int(ring_cy - ring_r) - 4
    y1 = int(ring_cy + ring_r) + 4
    for y in range(max(0, y0), min(size, y1)):
        row = y * size * 4
        for x in range(max(0, x0), min(size, x1)):
            px, py = x + 0.5, y + 0.5

            ring = abs(math.hypot(px - ring_cx, py - ring_cy) - ring_r) - thickness / 2.0
            line = draw_segment(x, y)
            for cx, cy in nodes:
                dot = sdf_circle(px, py, cx, cy, thickness * 1.75)
                blend(pixels, row + x * 4, WHITE, min(1.0, max(0.0, 0.5 - dot)) * 0.95)

            for dist in (ring, line):
                blend(pixels, row + x * 4, WHITE, min(1.0, max(0.0, 0.5 - dist)) * 0.75)

    return pixels


def write_png(path: str, size: int, pixels: bytearray) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    stride = size * 4
    raw = b"".join(b"\x00" + bytes(pixels[y * stride:(y + 1) * stride]) for y in range(size))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    payload = chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as file:  # noqa: PTH123
        file.write(b"\x89PNG\r\n\x1a\n" + payload)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "assets/icon.png"
    write_png(target, SIZE, render())
    print(f"Иконка сохранена: {target} ({SIZE}×{SIZE})")


if __name__ == "__main__":
    main()
