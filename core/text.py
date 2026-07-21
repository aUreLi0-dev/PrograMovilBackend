def clean_text(value):
    if not isinstance(value, str):
        return value

    has_mojibake = any(marker in value for marker in ('Ã', 'Â', 'â'))
    if has_mojibake:
        for encoding in ('cp1252', 'latin1'):
            try:
                return value.encode(encoding).decode('utf-8')
            except UnicodeError:
                continue
    return value


def clean_payload(value):
    if isinstance(value, dict):
        return {
            clean_text(key): clean_payload(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [clean_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(clean_payload(item) for item in value)
    return clean_text(value)
