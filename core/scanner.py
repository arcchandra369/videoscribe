import os
import subprocess
from datetime import datetime

from config import CLAMAV_ENABLED
from utils import logger
from utils.file_manager import quarantine_file


def _try_clamd_scan(filepath: str):
    try:
        import clamd
        cd = clamd.ClamdUnixSocket()
        cd.ping()
        result = cd.scan(filepath)
        return result
    except Exception:
        return None


def _clamscan_fallback(filepath: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["clamscan", "--no-summary", filepath],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return True, ""
        for line in result.stdout.splitlines():
            if "FOUND" in line:
                threat = line.split(":")[-1].replace("FOUND", "").strip()
                return False, threat
        return False, "Unknown threat"
    except FileNotFoundError:
        return None, "ClamAV not installed"
    except subprocess.TimeoutExpired:
        return None, "Scan timed out"


def scan_file(filepath: str) -> bool:
    ts = datetime.now().strftime("%H:%M:%S")

    if not CLAMAV_ENABLED:
        logger.warning("Virus scanning is disabled. Proceeding without scan.")
        return True

    logger.step("🔍", "Scanning for viruses...")

    result = _try_clamd_scan(filepath)

    if result is not None:
        status = result.get(filepath, ("ERROR", ""))
        if status[0] == "OK":
            logger.success("File passed ClamAV scan — no threats detected")
            return True
        elif status[0] == "FOUND":
            threat = status[1]
            dest = quarantine_file(filepath)
            logger.error(f"THREAT DETECTED: {threat}")
            logger.error(f"File quarantined to: {dest}")
            return False
    else:
        clean, threat = _clamscan_fallback(filepath)
        if clean is None:
            logger.warning(f"ClamAV unavailable: {threat}. Proceeding without scan.")
            return True
        elif clean:
            logger.success("File passed ClamAV scan — no threats detected")
            return True
        else:
            dest = quarantine_file(filepath)
            logger.error(f"THREAT DETECTED: {threat}")
            logger.error(f"File quarantined to: {dest}")
            return False
