import json
import os


PROFILES_FILE = "resume_profiles.json"


def load_all_profiles():

    if not os.path.exists(PROFILES_FILE):
        return {}

    try:

        with open(
            PROFILES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

            return {}

    except Exception:

        return {}


def save_profile(profile_name, resume_data):

    profiles = load_all_profiles()

    profiles[profile_name] = resume_data

    with open(
        PROFILES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profiles,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_profile(profile_name):

    profiles = load_all_profiles()

    return profiles.get(
        profile_name,
        {}
    )


def delete_profile(profile_name):

    profiles = load_all_profiles()

    if profile_name in profiles:

        del profiles[profile_name]

        with open(
            PROFILES_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                profiles,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    return False