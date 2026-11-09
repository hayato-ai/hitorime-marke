import shutil, os
from common import OUT, SCRATCH
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT + "css", exist_ok=True)
os.makedirs(OUT + "js", exist_ok=True)
shutil.copy(HERE + "/style.css", OUT + "css/style.css")
shutil.copy(HERE + "/main.js", OUT + "js/main.js")
shutil.copy(HERE + "/forms.js", OUT + "js/forms.js")
import build_index, build_others  # noqa: E402,F401
