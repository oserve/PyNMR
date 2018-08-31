# From https://gist.github.com/tomhennigan/5245713

def notify_delegates(method):
    """Decorator to call delegate methods. When decorating a method it will
    call `on_before_method_name` and `on_after_method_name`.

    Delegate methods are called before and after the actual method is called.
    On the after method the return value from the method is passed in as the
    `ret_value` keyword arg."""

    method_name = method.__name__

    # Figure out delegate method names.
    before_method = 'on_before_' + method_name
    exception_method = 'on_exception_in_' + method_name
    after_method = 'on_after_' + method_name

    def wrapper(self, *args, **kwargs):
        delegates = self.get_delegates_for_method(method_name)

        # Call the before methods.
        for delegate in delegates:
            if hasattr(delegate, before_method):
                getattr(delegate, before_method)(*args, **kwargs)

        try:
            return_value = method(self, *args, **kwargs)
        except Exception, e:
            kwargs['exception'] = e

            for delegate in delegates:
                if hasattr(delegate, exception_method):
                    getattr(delegate, exception_method)(*args, **kwargs)

            # Raise the exception.
            raise e

        # Call the after methods.
        kwargs['ret_value'] = return_value

        for delegate in delegates:
            if hasattr(delegate, after_method):
                getattr(delegate, after_method)(*args, **kwargs)

        return return_value

    return wrapper

class DelegateProviderMixin(object):
    """Mixin for a class that has delegates. Any method can be wrapped for
    delegates using the `@notify_delegates` decorator."""

    def __init__(self, *args, **kwargs):
        self.__delegates = []

    def add_delegate(self, delegate):
        """Adds a delegate specifically listening on all delegate methods it
        can respond to."""

        self.__delegates.append((delegate, None))

    def add_delegate_for_method(self, delegate, method):
        """Adds a delegate specifically listening on a certain method."""

        self.__delegates.append((delegate, [method]))

    def add_delegate_for_methods(self, delegate, methods):
        """Adds a delegate specifically listening on certain methods."""

        self.__delegates.append((delegate, methods))

    def remove_delegate(self, delegate):
        """Removes all hooks for the given delegate on the current object."""

        to_remove = []
        for index, (delegate_test, _methods) in enumerate(self.__delegates):
            if delegate == delegate_test:
                to_remove.append(index)

        for index in to_remove:
            del self.__delegates[index]

    def get_delegates_for_method(self, method):
        """Returns all delegates that are subscribed to all methods or to just
        the specific method. Delegates are returned in insertion order and only
        appear once regardless of how many times they have been added to this
        object."""

        delegates = []
        for delegate, delegate_methods in self.__delegates:
            if not delegate_methods or method in delegate_methods:
                if not delegate in delegates:
                    delegates.append(delegate)
        return delegates