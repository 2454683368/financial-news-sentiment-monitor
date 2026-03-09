from __future__ import annotations

import subprocess


def run(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=True)


def main() -> None:
    run('git add .')
    run('git commit -m "update daily report" || true')
    print('Local git commit step completed. Push manually or extend this script later.')


if __name__ == '__main__':
    main()
