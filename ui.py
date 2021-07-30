# Temporary placeholders for UI-generating functions. These currently don't do
# anything.

def render_text(fn):
    def wrapper():
        print("render_text")
        fn()
        print("done")
    return wrapper

def fluid_page(*args, **kwargs):
    return args

def text_output(name):
    return name

def slider_input(name):
    return name
