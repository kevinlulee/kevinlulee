# Define a custom metaclass by inheriting from type
class UpperCaseMeta(type):
    # __new__ is called before __init__ and is responsible for creating the class object
    def __new__(cls, name, bases, dct):
        # Iterate through the class dictionary (dct)
        uppercase_dct = {}
        for attr_name, attr_value in dct.items():
            # If the attribute is a string, convert it to uppercase
            if isinstance(attr_value, str):
                uppercase_dct[attr_name] = attr_value.upper()
            else:
                uppercase_dct[attr_name] = attr_value

        # Call the superclass (type) __new__ to create the class object
        return super().__new__(cls, name, bases, uppercase_dct)

# Define a class that uses the custom metaclass
class MyClass(metaclass=UpperCaseMeta):
    text_attribute = "hello world"
    number_attribute = 123
    another_text = "python is fun"

# Create an instance of MyClass (though the effect is on the class itself)
obj = MyClass()

# Access the class attributes to see the effect of the metaclass
print(MyClass.text_attribute)
print(MyClass.number_attribute)
print(MyClass.another_text)


# https://gemini.google.com/app/d92cf0f10c4b4ed9
# class decorators are less heavy. useful for quick and selective registrations
