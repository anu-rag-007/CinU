from urllib.parse import urlparse


SOCIAL_DOMAINS = {
    "instagram.com": "Instagram",
    "facebook.com": "Facebook",
    "x.com": "X",
    "twitter.com": "X",
    "tiktok.com": "TikTok",
    "youtube.com": "YouTube",
    "linkedin.com": "LinkedIn",
    "reddit.com": "Reddit",
}


SOCIAL_NAMES = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "twitter": "X",
    "tiktok": "TikTok",
    "youtube": "YouTube",
    "linkedin": "LinkedIn",
    "reddit": "Reddit",
}


def get_hostname(value):
    if not value:
        return ""

    try:
        hostname = urlparse(value).hostname

        if not hostname:
            return ""

        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except Exception:
        return ""


def platform_from_url(value):
    hostname = get_hostname(value)

    for domain, platform in SOCIAL_DOMAINS.items():

        if hostname == domain:
            return platform

        if hostname.endswith("." + domain):
            return platform

    return None


def platform_from_text(value):
    if not value:
        return None

    text = str(value).lower()

    for name, platform in SOCIAL_NAMES.items():

        if name in text:
            return platform

    return None


def identify_source(result):

    # Check all likely URL fields
    possible_urls = [
        result.get("link"),
        result.get("url"),
        result.get("serpapi_link"),
        result.get("source_url"),
        result.get("displayed_link"),
    ]

    for value in possible_urls:

        platform = platform_from_url(value)

        if platform:
            return platform

    # Finally inspect source text
    platform = platform_from_text(
        result.get("source")
    )

    if platform:
        return platform

    return "Web"


def get_direct_url(result):

    possible_urls = [
        result.get("url"),
        result.get("serpapi_link"),
        result.get("source_url"),
        result.get("link"),
    ]

    for value in possible_urls:

        if not value:
            continue

        if "google.com/goto" in value.lower():
            continue

        if platform_from_url(value):
            return value

    return None


def parse_result(result, result_type):

    link = result.get("link")

    direct_url = get_direct_url(result)

    redirect_url = None

    if link and "google.com/goto" in link.lower():
        redirect_url = link

    return {
        "title": result.get(
            "title",
            "Untitled"
        ),

        "url": direct_url,

        "redirect_url": redirect_url,

        "url_resolved": direct_url is not None,

        "source": identify_source(result),

        "type": result_type,

        "thumbnail": result.get(
            "thumbnail"
        ),

        "displayed_link": result.get(
            "displayed_link"
        ),

        "raw_source": result.get(
            "source"
        ),
    }


def extract_results(lens_results):

    discovered = []

    for result in lens_results.get(
        "exact_matches",
        []
    ):

        parsed = parse_result(
            result,
            "exact_match"
        )

        discovered.append(parsed)

    for result in lens_results.get(
        "visual_matches",
        []
    ):

        parsed = parse_result(
            result,
            "visual_match"
        )

        discovered.append(parsed)

    return discovered


def is_social_result(result):

    return result.get("source") != "Web"


def prioritize_social_results(results):

    return sorted(
        results,
        key=lambda result: (
            result.get("type") != "exact_match",
            not result.get("url_resolved"),
        )
    )


def find_social_matches(lens_results):

    results = extract_results(
        lens_results
    )

    social_results = [
        result
        for result in results
        if is_social_result(result)
    ]

    return prioritize_social_results(
        social_results
    )


def find_best_social_match(lens_results):

    social_results = find_social_matches(
        lens_results
    )

    if not social_results:
        return None, []

    return social_results[0], social_results