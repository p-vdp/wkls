import sys
from .core import Wkl

# Replace the module with an instance of Wkls
sys.modules[__name__] = Wkl()
