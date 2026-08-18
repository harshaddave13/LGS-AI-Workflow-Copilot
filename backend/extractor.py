import re


def extract_lgs_requirements(text: str) -> dict:
    """
    Simple rule-based MVP extractor.

    We will replace/enhance this later with an LLM,
    but this gives us a reliable first structured output.
    """

    result = {
        "fire_rating": None,
        "acoustic_rating": None,
        "steel_thickness": None,
        "stud_spacing": None,
        "wall_height": None,
        "system_type": None,
        "missing_information": []
    }

    # Fire rating
    fire_match = re.search(
        r"(\d{2,3})\s*(?:minute|min)\s*(?:fire|fire resistance)",
        text,
        re.IGNORECASE
    )
    if fire_match:
        result["fire_rating"] = f"{fire_match.group(1)} minutes"

    # Acoustic rating
    acoustic_match = re.search(
        r"(\d{2,3})\s*dB",
        text,
        re.IGNORECASE
    )
    if acoustic_match:
        result["acoustic_rating"] = f"{acoustic_match.group(1)} dB"

    # Steel thickness
    thickness_match = re.search(
        r"(\d+(?:\.\d+)?)\s*mm\s*(?:steel|thick|thickness)",
        text,
        re.IGNORECASE
    )
    if thickness_match:
        result["steel_thickness"] = f"{thickness_match.group(1)} mm"

    # Stud spacing
    spacing_match = re.search(
        r"(\d{3,4})\s*mm\s*(?:centres|centers|c\/c)",
        text,
        re.IGNORECASE
    )
    if spacing_match:
        result["stud_spacing"] = f"{spacing_match.group(1)} mm"

    # Wall height
    height_match = re.search(
        r"(?:wall height|height)[^\d]{0,10}(\d+(?:\.\d+)?)\s*(m|mm)",
        text,
        re.IGNORECASE
    )
    if height_match:
        result["wall_height"] = (
            f"{height_match.group(1)} {height_match.group(2)}"
        )

    # Basic system classification
    lowered = text.lower()

    if "partition" in lowered:
        result["system_type"] = "LGS Partition"
    elif "external wall" in lowered:
        result["system_type"] = "External LGS Wall"
    elif "light gauge steel" in lowered or "lgs" in lowered:
        result["system_type"] = "Light Gauge Steel System"

    # Missing information
    for key in [
        "fire_rating",
        "acoustic_rating",
        "steel_thickness",
        "stud_spacing",
        "wall_height"
    ]:
        if not result[key]:
            result["missing_information"].append(key)

    return result