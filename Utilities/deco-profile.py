import cProfile


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args)
            profile.disable()
            return result
        finally:
            profile.dump_stats('profile.cprof')
    return profiled_func
