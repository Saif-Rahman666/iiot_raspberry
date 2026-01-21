import sys
import types
import importlib.util

# Create a more complete 'imp' shim for Python 3.13
imp_shim = types.ModuleType('imp')

def find_module(name, path=None):
    spec = importlib.util.find_spec(name, path)
    if spec is None:
        raise ImportError(f"No module named {name}")
    return None, None, None # Flatbuffers ignores these return values anyway

imp_shim.find_module = find_module
imp_shim.reload = importlib.reload

# Inject it into the system before TensorFlow loads
sys.modules['imp'] = imp_shim
print(" Advanced Python 3.13 shim applied (imp.find_module ready)")
