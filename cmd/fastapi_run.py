from .main import core
from internal.server import get_app

app = get_app(lambda: core)