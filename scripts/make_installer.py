import sys

sys.path.append("..")
import datetime
import os
import subprocess
from shutil import rmtree
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path
import platform


ROOT_DIR = Path("./../.")
SPEC_FILENAME = ROOT_DIR / "build_app.spec"


GIT_CURRENT_BRANCH = (
    subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
)

GIT_HASH = (
    subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
)

GIT_HASH_full = (
    subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
)

# GIT_CLOSEST_TAG = (
#     subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
#     .decode()
#     .strip()
# )

# GIT_CLOSEST_TAG_DATE = (
#     subprocess.check_output(["git", "log", "-1", "--format=%ai", GIT_CLOSEST_TAG])
#     .decode()
#     .strip()
#     .split(" ")[0]
# )


PYINSTALLER_VERSION = (
    subprocess.check_output(
        [str(Path(ROOT_DIR / ".venv/Scripts/pyinstaller.exe")), "-v"]
    )
    .decode()
    .strip()
)


def create_about_file():
    with open(ROOT_DIR / "ABOUT", "w") as f:
        f.writelines(
            [
                f"datetime of build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"platform: {platform.platform()}\n",
                f"version Python: {sys.version}\n",
                f"version Pyinstaller: {PYINSTALLER_VERSION}\n",
                # f"version EDO app: {GIT_CLOSEST_TAG} (date={GIT_CLOSEST_TAG_DATE})\n",
                # f"revision EDO app: {GIT_HASH}\n",
                # f"revision (full) EDO app: {GIT_HASH_full}\n",
                # f"current branch: {GIT_CURRENT_BRANCH}\n",
            ]
        )


def create_zip():
    print("creating Zip File")
    distPath = ROOT_DIR / "pyinstaller_builds/dist/EDO Coach App"

    zipPath = ROOT_DIR / "builds"

    # delete large unused Qt6WebEngineCore.dll of PySide6
    os.remove(distPath / "PySide6\\Qt6WebEngineCore.dll")

    if not zipPath.exists():
        os.makedirs(zipPath)

    date_time_str = datetime.datetime.now().strftime("%Y%m%d")
    buildName = f"{date_time_str}_EDO_COACH_APP_{GIT_CLOSEST_TAG}_{GIT_HASH}.zip"
    fNameZip = zipPath / buildName

    with ZipFile(fNameZip, "w", ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(distPath):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file), os.path.join(distPath, "..")
                    ),
                )
    print("Done!")


def build_exe():
    print("> running pyinstaller")
    try:
        rmtree(".\\dist")
        rmtree(".\\build")
    except Exception as e:
        print(e)

    subprocess.call([".\\..\\.venv\\Scripts\\pyinstaller.exe", str(SPEC_FILENAME)])
    print("> Done!")


if __name__ == "__main__":
    os.chdir(ROOT_DIR)
    # create_about_file()


    os.chdir(".\\pyinstaller_builds")
    build_exe()
    # create_zip()
