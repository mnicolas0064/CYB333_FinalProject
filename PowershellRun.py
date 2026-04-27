import platform
import shutil
import subprocess
import requests
from pathlib import Path

INPUT_FILE = Path("hosts.txt")
PS_SCRIPT = Path("scanupdatesoffline.ps1")
OUTPUT_FILE = Path("reachable_hosts.txt")
PING_COUNT = 1
PING_TIMEOUT_MS = 1000
PS_TIMEOUT_SEC = 3600
url = 'https://catalog.s.download.windowsupdate.com/microsoftupdate/v6/wsusscan/wsusscn2.cab'
response = requests.get(url)

if response.status_code == 200:
    with open('wsusscn2.cab', 'wb') as f:
        f.write(response.content)

def ping_host(host: str, count: int = PING_COUNT, timeout_ms: int = PING_TIMEOUT_MS) -> bool:
    system = platform.system().lower()
    timeout_sec = max(1, timeout_ms // 1000)

    if system == "windows":
        args = ["ping", "-n", str(count), "-w", str(timeout_ms), host]
    else:
        args = ["ping", "-c", str(count), "-W", str(timeout_sec), host]

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_sec + 3,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def load_hosts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Hosts file not found: {path}")
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.strip().startswith("#")]


def find_powershell() -> list[str] | None:
    candidates = ["powershell.exe", "pwsh", "powershell"]
    for exe in candidates:
        if shutil.which(exe):
            return [exe]
    return None


def execute_powershell_script(script_path: Path, host: str, timeout_sec: int = PS_TIMEOUT_SEC) -> bool:
    pwsh = find_powershell()
    if not pwsh:
        print("Warning: PowerShell executable not found. Skipping script execution.")
        return False

    if not script_path.exists():
        print(f"Warning: PowerShell script not found: {script_path}")
        return False

    args = [*pwsh, "-NoProfile", "-File", str(script_path), host, ">>" , "updates.txt"]
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"PowerShell script timed out after {timeout_sec} seconds for {host}.")
        return False
    except FileNotFoundError:
        print("PowerShell executable was not found while attempting to run the script.")
        return False


def main() -> None:
    hosts = load_hosts(INPUT_FILE)
    reachable = []

    for host in hosts:
        print(f"Pinging {host}...")
        if ping_host(host):
            print(f"  SUCCESS: {host}")
            reachable.append(host)
            print(f"  Executing {PS_SCRIPT} for {host}...")
            script_ok = execute_powershell_script(PS_SCRIPT, host)
            print(f"  PowerShell script {'SUCCEEDED' if script_ok else 'FAILED'} for {host}")
        else:
            print(f"  FAILED: {host}")

    OUTPUT_FILE.write_text("\n".join(reachable) + ("\n" if reachable else ""), encoding="utf-8")
    print(f"\nWrote {len(reachable)} reachable host(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
