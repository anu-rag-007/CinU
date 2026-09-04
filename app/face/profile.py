def get_profile_by_id(registry, profile_id):
    for profile in registry:
        if profile["profile_id"] == profile_id:
            return profile
    return None