#!/usr/bin/env python3
import subprocess
from pathlib import Path

from tqdm import tqdm

PHNBASE = Path("storage/emulated/0/Documents/Transfer")
FROMDIR = Path("Alice-no-Takarabako")


def run_cmd(cmd: list[str]) -> None:
    sp = subprocess.run(cmd, capture_output=True)
    if sp.returncode != 0:
        raise RuntimeError(
            f"\n\tcommand: {sp.args}"
            f"\n\tstdout:  {sp.stdout.decode("utf-8")}"
            f"\n\tstderr:  {sp.stderr.decode("utf-8")}"
        )
    return


def main() -> None:
    print(f"Exploring: {FROMDIR}")
    raw_paths: list[Path] = [x for x in tqdm(FROMDIR.glob("**/*"))]
    dirs: list[Path] = [x for x in raw_paths if x.is_dir()]
    files: list[Path] = [x for x in raw_paths if x.is_file()]
    print("Making Directories")
    for dir in tqdm(dirs):
        phn_dir: str = '"' + str(PHNBASE / dir) + '"'
        run_cmd(["adb", "shell", "mkdir", "-p", phn_dir])
    print("Transferring Files")
    for file in tqdm(files):
        phn_parent: str = (
            str(PHNBASE / Path(file).parent)
            if Path(file).parent != PHNBASE
            else str(PHNBASE)
        )
        run_cmd(["adb", "push", str(file), phn_parent])
    return


if __name__ == "__main__":
    main()
