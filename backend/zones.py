"""Location Mapping Module: turn a pixel position into a zone name.

The camera frame is split into a 2 x 2 grid:
    Zone A | Zone B
    -------+-------
    Zone C | Zone D
"""
from config import ZONE_NAMES


def get_zone(center_x, center_y, frame_width, frame_height):
    col = 0 if center_x < frame_width / 2 else 1
    row = 0 if center_y < frame_height / 2 else 1
    return ZONE_NAMES[row * 2 + col]
