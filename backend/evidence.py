import re


def find_evidence(pages, value):
    """
    Find the page and sentence containing an extracted value.
    """

    if not value:
        return None

    # Extract first number-like token from value
    match = re.search(r"\d+(?:\.\d+)?", value)

    if not match:
        return None

    search_value = match.group(0)

    for page in pages:

        text = page["text"]

        # Basic sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:

            if search_value.lower() in sentence.lower():

                return {
                    "page": page["page"],
                    "evidence": sentence.strip()
                }

    return None