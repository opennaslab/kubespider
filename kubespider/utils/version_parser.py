def check_version_at_lest(current_version: str, target_version: str) -> bool:
    if current_version == target_version:
        return True
    current_version = parse_version(current_version)
    target_version = parse_version(target_version)
    index = 0
    while True:
        if len(current_version) <= index or len(target_version) <= index:
            return False
        if current_version[index] > target_version[index]:
            return True
        index += 1


def parse_version(version_name: str) -> list[int]:
    return [int(x) for x in version_name.split('.')]
