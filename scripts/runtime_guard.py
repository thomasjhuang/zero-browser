"""Bound an owned CLI worker without importing the inference runtime."""

import ctypes
import fcntl
import os
import re
import signal
import subprocess
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path


class RUsage(ctypes.Structure):
    # Layout from macOS sys/resource.h, rusage_info_v0.
    _fields_ = [("uuid", ctypes.c_uint8 * 16)] + [
        (name, ctypes.c_uint64) for name in (
            "user_time", "system_time", "idle_wakeups", "interrupt_wakeups", "pageins",
            "wired_size", "resident_size", "phys_footprint", "start_time", "exit_time",
        )
    ]


def process_memory(pid):
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    call = library.proc_pid_rusage
    call.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
    call.restype = ctypes.c_int
    info = RUsage()
    if call(pid, 0, ctypes.byref(info)) != 0:
        raise OSError(ctypes.get_errno(), "Cannot read the worker memory footprint")
    return info.phys_footprint


def worker_memory_limit():
    total = int(subprocess.check_output(["/usr/sbin/sysctl", "-n", "hw.memsize"], text=True))
    pressure = subprocess.check_output(["/usr/bin/memory_pressure", "-Q"], text=True)
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    if not match:
        raise RuntimeError("Cannot read memory headroom. No inference worker started.")
    headroom = total * int(match[1]) // 100
    budget = min(6 * 2**30, total // 3, headroom - 2 * 2**30)
    if budget < 3 * 2**30:
        raise RuntimeError("Insufficient memory headroom for Qwen. Close unused applications before another run.")
    return budget


@contextmanager
def cleanup_signals():
    # Further Ctrl-C presses must not interrupt cleanup of owned processes.
    main_thread = threading.current_thread() is threading.main_thread()
    previous = signal.signal(signal.SIGINT, signal.SIG_IGN) if main_thread else None
    try:
        yield
    finally:
        if main_thread:
            signal.signal(signal.SIGINT, previous)


def stop_process_group(process, grace=1):
    """Stop only the group created with start_new_session=True."""
    with cleanup_signals():
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=grace)


def supervise(command, *, timeout, memory_limit, memory_reader=process_memory):
    process = subprocess.Popen(command, start_new_session=True)
    deadline = time.monotonic() + timeout
    try:
        while process.poll() is None:
            if time.monotonic() >= deadline:
                raise RuntimeError("Worker deadline reached. The owned run stopped.")
            try:
                footprint = memory_reader(process.pid)
            except OSError:
                if process.poll() is not None:
                    break
                raise
            if footprint > memory_limit:
                raise RuntimeError("Worker memory budget exceeded. The owned run stopped.")
            time.sleep(0.1)
        return process.wait()
    finally:
        stop_process_group(process)


@contextmanager
def single_run():
    path = Path(tempfile.gettempdir()) / f"zero-browser-{os.getuid()}.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another zero-browser CLI run is active. Stop it before starting another.") from None
        yield
    finally:
        os.close(fd)


def challenge_reason(page):
    text = " ".join(page.get("text", "").casefold().split())
    phrases = (
        "verify you are human", "verify that you are human", "confirm you are human",
        "confirm that you are human", "our systems have detected unusual traffic",
        "please complete the captcha", "complete the security check",
    )
    if any(phrase in text for phrase in phrases):
        return "Human verification is required. The CLI stopped."
    return None
