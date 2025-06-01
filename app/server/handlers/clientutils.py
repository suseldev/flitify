def disable_timeout(sockAttr = 'socket'):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            soc = getattr(self.connection, sockAttr)
            originalTimeout = soc.gettimeout()
            soc.settimeout(None)
            try:
                return func(self, *args, **kwargs)
            finally:
                soc.settimeout(originalTimeout)
        return wrapper
    return decorator
