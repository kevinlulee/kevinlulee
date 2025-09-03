def collect_class_property_names(cls):
    # collect property names across the MRO without hasattr/try/except
    props = set()
    for base in cls.__mro__:
        for name, val in base.__dict__.items():
            if isinstance(val, property):
                props.add(name)
    return props
