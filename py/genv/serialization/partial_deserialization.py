
# TODO: give it a better name
def smart_ctor(instance, *args_dict, **kwargs):
    """
    This function is a generic ctor allowing for deserializing of a partial representation of the object
        as well as the dataclass default usage. Either args_dict or kwargs expected.
    :param instance: object self
    :param args_dict: Optional. A tuple containing a dict of the instance property names to values.
    :param kwargs: kwargs args for the object initialization.
    """
    if len(args_dict) == 1 and type(args_dict[0]) is dict:
        for arg_dict_item in args_dict[0].items():
            instance.__dict__[arg_dict_item[0]] = arg_dict_item[1]
    elif kwargs:
        instance.__dict__ = kwargs.copy()

    # Complete non-given items with the default of None
    property_names = instance.__class__.__dict__['__dataclass_fields__'].keys()
    for property_name in property_names:
        if property_name not in instance.__dict__:
            instance.__dict__[property_name] = None