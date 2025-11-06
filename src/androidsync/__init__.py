from argparse import ArgumentParser
from pathlib import Path
from subprocess import run

from tqdm import tqdm


def run_cmd(cmd: list[str]) -> tuple[int, str, str, str]:
    sp = run(cmd, capture_output=True)
    return sp.returncode, sp.args, sp.stdout.decode("utf-8"), sp.stderr.decode("utf-8")


def ensure_cmd(stuff: tuple[int, str, str, str]) -> None:
    ret, args, out, err = stuff
    if ret != 0:
        raise RuntimeError(
            f"\n\tcommand: {args}" f"\n\tstdout:  {out}" f"\n\tstderr:  {err}"
        )


def push_file(file: Path, fromparent: Path, phnbase: Path) -> None:
    full_par = (
        file.parent.relative_to(fromparent)
        if file.parent.is_relative_to(fromparent)
        else file.parent
    )
    phn_parent = phnbase / full_par
    if phn_parent == file:
        raise RuntimeError(phn_parent)
    ensure_cmd(run_cmd(["adb", "shell", "mkdir", "-p", '"' + str(phn_parent) + '"']))
    ensure_cmd(run_cmd(["adb", "push", str(file), str(phn_parent)]))


def main() -> None:
    parser = ArgumentParser(
        prog="androidsync",
        description="Android phone syncronisation utility",
    )
    parser.add_argument(
        "action",
        default="push",
        choices=["push", "pull"],
    )
    parser.add_argument(
        "--fromdir",
        default="SyncFolder",
        help="base directory of backups",
    )
    parser.add_argument(
        "--phnbase",
        default="storage/emulated/0",
        help="base directory on the phone",
    )
    args = parser.parse_args()

    fromdir = Path(args.fromdir)
    phnbase = Path(args.phnbase)
    fromparent = Path(fromdir.parent)
    action = args.action.lower()
    if action == "push":
        files = [
            x
            for x in Path(fromdir).glob("**/*")
            if x.is_file() and ".thumbnail" not in str(x)
        ]
        print("Pushing Files")
        [push_file(file, fromparent, phnbase) for file in tqdm(files)]  # type: ignore[func-returns-value]
    elif action == "pull":
        print("Pulling Files")
        ret, _, out, _ = run_cmd(["adb", "shell", "ls", str(phnbase)])
        if ret != 0:
            raise (RuntimeError)
        run_cmd(["adb", "pull", f"{phnbase}", str(fromdir)]),
    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
