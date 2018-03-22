def deep_get(dict_, key, default_value=None):
    try:
        keys = key.split('.')
        iterative_dict = dict_
        for k in keys:
            iterative_dict = iterative_dict[k]
        return iterative_dict
    except KeyError:
        return default_value
    except AttributeError:
        return default_value
