SENSITIVE_KEYS={'email','phone','bank','account_number','secret','token','raw_message','customer_name'}
def assert_public_safe(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in SENSITIVE_KEYS and v not in (None,'','SYNTHETIC'): raise ValueError(f'sensitive field: {k}')
            assert_public_safe(v)
    elif isinstance(obj,list):
        for x in obj: assert_public_safe(x)
    return True
