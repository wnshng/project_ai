"""
색상 이론 기반 코디 추천 알고리즘
- 톤온톤(Tone on Tone): 같은 색상 계열의 명도/채도 변형
- 보색(Complementary): 색상환에서 반대편 색상으로 대비
- 유사색(Analogous): 인접한 색상으로 조화
HEX 값을 HSV로 변환하여 각 규칙에 맞는 조합을 점수화하고 추천.
"""

import math
from typing import Optional

# 색상환에서 Hue 각도 (0~360). 보색 = +180, 유사색 = ±30 정도
HUE_WHEEL = 360


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """#RRGGBB -> (r, g, b) 0-255"""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return (0, 0, 0)
    return (
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """(r,g,b) 0-255 -> #RRGGBB"""
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """RGB 0-255 -> HSV: H 0-360, S 0-1, V 0-1"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    d = mx - mn
    v = mx
    s = 0.0 if mx == 0 else d / mx
    if d == 0:
        h = 0.0
    elif mx == r:
        h = 60 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60 * ((b - r) / d + 2)
    else:
        h = 60 * ((r - g) / d + 4)
    if h < 0:
        h += 360
    return (h, s, v)


def hex_to_hsv(hex_str: str) -> tuple[float, float, float]:
    """HEX -> HSV (H 0-360, S 0-1, V 0-1)"""
    r, g, b = hex_to_rgb(hex_str)
    return rgb_to_hsv(r, g, b)


def hue_distance(h1: float, h2: float) -> float:
    """색상환 위 두 Hue 사이 최단 각도 차이 (0~180)"""
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def score_tone_on_tone(hex1: str, hex2: str) -> float:
    """
    톤온톤: 같은 색상 계열(비슷한 Hue), 명도/채도만 다르면 높은 점수.
    Hue 차이가 작고, S/V 차이가 있으면 좋음.
    """
    h1, s1, v1 = hex_to_hsv(hex1)
    h2, s2, v2 = hex_to_hsv(hex2)
    hue_diff = hue_distance(h1, h2)
    # Hue가 가까울수록 좋음 (30도 이내)
    hue_score = max(0, 1 - hue_diff / 30.0)
    # S 또는 V 차이가 있으면 톤온톤 느낌
    sv_diff = abs(s1 - s2) + abs(v1 - v2)
    sv_score = min(1.0, sv_diff * 2)
    return 0.7 * hue_score + 0.3 * sv_score


def score_complementary(hex1: str, hex2: str) -> float:
    """
    보색 대비: 색상환에서 약 180도 차이일수록 높은 점수.
    """
    h1, _, _ = hex_to_hsv(hex1)
    h2, _, _ = hex_to_hsv(hex2)
    d = hue_distance(h1, h2)
    # 180도에 가까울수록 좋음 (150~210도 구간)
    if 150 <= d <= 210:
        return 1.0 - abs(d - 180) / 30.0
    return max(0, 0.5 - abs(d - 180) / 180.0)


def score_analogous(hex1: str, hex2: str) -> float:
    """
    유사색: Hue가 30~60도 정도 차이일 때 조화.
    """
    h1, _, _ = hex_to_hsv(hex1)
    h2, _, _ = hex_to_hsv(hex2)
    d = hue_distance(h1, h2)
    if 20 <= d <= 70:
        return 1.0 - abs(d - 45) / 45.0
    return max(0, 0.5 - d / 90.0)


def score_outfit(
    items: list[dict],
    recommendation_type: str,
) -> float:
    """
    한 벌 코디(여러 아이템)에 대해 타입별로 점수 합산.
    items: [ {"primary_color_hex": "#..." }, ... ]
    """
    if len(items) < 2:
        return 0.5
    hexes = [it.get("primary_color_hex") for it in items if it.get("primary_color_hex")]
    if len(hexes) < 2:
        return 0.5
    total = 0.0
    count = 0
    for i in range(len(hexes)):
        for j in range(i + 1, len(hexes)):
            if recommendation_type == "tone_on_tone":
                total += score_tone_on_tone(hexes[i], hexes[j])
            elif recommendation_type == "complementary":
                total += score_complementary(hexes[i], hexes[j])
            elif recommendation_type == "analogous":
                total += score_analogous(hexes[i], hexes[j])
            else:
                total += (
                    score_tone_on_tone(hexes[i], hexes[j]) * 0.33
                    + score_complementary(hexes[i], hexes[j]) * 0.33
                    + score_analogous(hexes[i], hexes[j]) * 0.34
                )
            count += 1
    return total / count if count else 0.0
