import shutil, os
from common import OUT, SCRATCH
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT + "css", exist_ok=True)
os.makedirs(OUT + "js", exist_ok=True)
shutil.copy(HERE + "/style.css", OUT + "css/style.css")
shutil.copy(HERE + "/main.js", OUT + "js/main.js")
shutil.copy(HERE + "/forms.js", OUT + "js/forms.js")
shutil.copytree(HERE + "/img", OUT + "img", dirs_exist_ok=True)
import build_index, build_others  # noqa: E402,F401
# プロフィールのページは無くした（担当者の内容は index に集約）
if os.path.exists(OUT + "profile.html"):
    os.remove(OUT + "profile.html")
