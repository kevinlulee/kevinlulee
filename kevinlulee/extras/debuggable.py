from __future__ import annotations
import kevinlulee as kx


def debuggable(*method_pairs):
    """
    Class decorator that redirects method calls when self.debug is True.
    Usage: @debuggable('execute', 'build') redirects execute() to build() when self.debug == True
    """

    def decorator(cls):
        # Process pairs of methods (original, replacement)
        for i in range(0, len(method_pairs), 2):
            if i + 1 >= len(method_pairs):
                raise ValueError(
                    f"debug decorator requires pairs of method names"
                )

            original_name = method_pairs[i]
            replacement_name = method_pairs[i + 1]

            # Get the original method
            if not hasattr(cls, original_name):
                raise AttributeError(
                    f"Class {cls.__name__} has no method '{original_name}'"
                )

            original_method = getattr(cls, original_name)

            # Create wrapper that checks self.debug
            def make_wrapper(orig_name, repl_name, orig_method):
                def wrapper(self, *args, **kwargs):
                    if self.debug or nvim.g.debug:
                        replacement_method = getattr(self, repl_name)
                        return replacement_method(*args, **kwargs)
                    else:
                        return orig_method(self, *args, **kwargs)

                wrapper.__name__ = orig_method.__name__
                wrapper.__doc__ = orig_method.__doc__
                return wrapper

            # Replace the method with the wrapper
            setattr(
                cls,
                original_name,
                make_wrapper(original_name, replacement_name, original_method),
            )

        # Add set_debug method to the class
        def set_debug(self, value):
            if value is None:
                return
            self.debug = value
            return self

        cls.set_debug = set_debug
        cls.debug = False
        cls.debuggable = True

        return cls

    return decorator
