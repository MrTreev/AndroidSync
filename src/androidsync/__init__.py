import subprocess
from argparse import ArgumentParser
from pathlib import Path

from tqdm import tqdm

PHNBASE = Path("storage/emulated/0/Documents/Transfer")
FROMDIR = Path("SyncFolder")


def run_cmd(cmd: list[str]) -> None:
    sp = subprocess.run(cmd, capture_output=True)
    if sp.returncode != 0:
        raise RuntimeError(
            f"\n\tcommand: {sp.args}"
            f"\n\tstdout:  {sp.stdout.decode("utf-8")}"
            f"\n\tstderr:  {sp.stderr.decode("utf-8")}"
        )
    return


def nopar(dir) -> str:
    return str(dir).rpartition("../")[-1]


def main() -> None:
    global FROMDIR, PHNBASE
    parser = ArgumentParser(prog="androidsync")
    parser.add_argument("fromdir", default=FROMDIR)
    parser.add_argument("--phnbase", default=PHNBASE)
    args = parser.parse_args()
    FROMDIR = Path(args.fromdir)
    PHNBASE = Path(args.phnbase)
    print(f"Exploring: {FROMDIR}")
    raw_paths: list[Path] = [x for x in tqdm(FROMDIR.glob("**/*"))]
    dirs: list[Path] = [x for x in raw_paths if x.is_dir()]
    files: list[Path] = [x for x in raw_paths if x.is_file()]
    print("Making Directories")
    for dir in tqdm(dirs):
        phn_dir: str = '"' + str(PHNBASE / nopar(dir)) + '"'
        run_cmd(["adb", "shell", "mkdir", "-p", phn_dir])
    print("Transferring Files")
    for file in tqdm(files):
        phn_parent: str = (
            str(PHNBASE / nopar(Path(file).parent))
            if Path(file).parent != PHNBASE
            else str(PHNBASE)
        )
        run_cmd(["adb", "push", str(file), phn_parent])
    return


if __name__ == "__main__":
    main()
