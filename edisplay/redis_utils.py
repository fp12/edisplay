def redis_to_int(value):
    return int(value or 0)


def redis_to_bool(value):
    return bool(redis_to_int(value))
