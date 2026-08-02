def get_source_url(source_str):
    """
    Utility function mapping source strings to actual web URLs.
    Preserved for edge-case unit testing and backwards-compatibility.
    """
    if not isinstance(source_str, str):
        return "https://blinkit.com"
    source_lower = source_str.lower().strip()
    if "play.google.com" in source_lower or "playstore" in source_lower or "google play" in source_lower:
        return "https://play.google.com/store/apps/details?id=com.grofers.customerapp"
    elif "apps.apple.com" in source_lower or "appstore" in source_lower or "app store" in source_lower:
        return "https://apps.apple.com/in/app/blinkit-grocery-delivery/id960984733"
    elif "youtube.com" in source_lower or "youtu.be" in source_lower:
        return source_str
    elif "mouthshut" in source_lower:
        return "https://www.mouthshut.com/product-reviews/Blinkit-reviews-925763914"
    elif "trustpilot" in source_lower:
        return "https://www.trustpilot.com/review/blinkit.com"
    elif "reddit" in source_lower:
        return "https://www.reddit.com/r/india/"
    elif source_str.startswith("http"):
        return source_str
    return "https://blinkit.com"
