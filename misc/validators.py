def validate_email(data: str) -> bool | str:
    if data.count('@') == 1:
        if data.startswith('@') or data.endswith('@'):
            return False
        name, domain = data.split('@')
        if '.' not in domain:
            return False
        domain_name, domain_postfix = domain.rsplit('.', 1)
        if len(domain_postfix) <= 1:
            return False
        email = f'{name}@{domain_name}.{domain_postfix}'
        if len(email) <= 34:
            return email
    return False


def validate_phone(data: str) -> bool | str:
    if isinstance(data, str):
        validated_phone = '+' if data.startswith('+') else ''
        for ch in data:
            if ch.isdigit():
                validated_phone += ch
        if validated_phone.startswith('8'):
            validated_phone = '+7' + validated_phone[1:]
        if len(validated_phone) == 12:
            return validated_phone
    return False


def validate_passport(data: str) -> str | bool:
    if isinstance(data, str):
        validated_passport = ''
        digit = 0
        for ch in data:
            if ch.isdigit():
                validated_passport += ch
                digit += 1
            if digit == 4:
                validated_passport += ' '
        if len(validated_passport) == 11:
            return validated_passport
    return False
