from decimal import Decimal


DAY_NAMES = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miercoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sabado',
    7: 'Domingo',
}

ROLE_NAMES = {
    'delegate': 'delegado',
    'subdelegate': 'subdelegado',
}


def api_response(message, data=None, success=True, error=None):
    return {
        'message': message,
        'data': data,
        'success': success,
        'error': error,
    }


def decimal_to_int(value):
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)


def decimal_to_float(value):
    if value is None:
        return None
    return float(value)


def format_date(value):
    if not value:
        return ''
    return value.strftime('%d/%m/%Y')


def format_time(value):
    if not value:
        return ''
    return value.strftime('%H:%M')


def day_name(day_of_week):
    return DAY_NAMES.get(day_of_week, str(day_of_week))


def role_name(position):
    return ROLE_NAMES.get(position, 'estudiante')


def split_full_name(full_name):
    parts = (full_name or '').strip().split()
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    if len(parts) == 2:
        return parts[0], parts[1]
    return ' '.join(parts[:-2]), ' '.join(parts[-2:])


def teacher_to_dict(teacher):
    if not teacher:
        return None
    first_name, last_name = split_full_name(teacher.full_name)
    return {
        'code': teacher.teacher_code,
        'firstName': first_name,
        'lastName': last_name,
        'fullName': teacher.full_name,
        'institutionalEmail': teacher.institutional_email,
    }


def user_to_dict(user):
    if not user:
        return None
    first_name, last_name = split_full_name(user.full_name)
    return {
        'code': user.code,
        'firstName': first_name,
        'lastName': last_name,
        'full_name': user.full_name,
        'institutional_email': user.institutional_email,
    }
