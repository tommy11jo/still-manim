from smanim import *


# Minor issue but I'm not sure if we want np and others to be imported (manim imports them but might lead to confusing namespace issues)
def test():
    n = np.array([1, 2])
    print(n)


test()
