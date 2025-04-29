import functools

class Parent:
    @staticmethod
    def my_decorator(func):
    @staticmethod
    def my_decorator(func):
        """
        This is a decorator method defined in the Parent class.
        It adds some behavior before and after the decorated function.
        """
        @functools.wraps(func) # Preserve the original function's metadata
        def wrapper(self, *args, **kwargs):
            print("--- Before calling the decorated method (from Parent decorator) ---")
            result = func(self, *args, **kwargs)
            print("--- After calling the decorated method (from Parent decorator) ---")
            return result
        return wrapper

class Child(Parent):
    # it is necessary to prefix "Parent" or it doesnt work

    # @my_decorator # (doesnt work)

    @Parent.my_decorator
    def child_method(self, message):
        """
        This method in the Child class is decorated by a method from the Parent class.
        """
        print(f"Executing child_method with message: {message}")
        return f"Processed: {message}"

# --- Demonstration ---

print("Creating a Child instance and calling the decorated method:")
child_instance = Child()
output = child_instance.child_method("Hello from Child!")

print(f"\nReturn value of child_method: {output}")
