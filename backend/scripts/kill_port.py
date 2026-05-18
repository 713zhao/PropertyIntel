import os
import signal
import sys


def kill_process(pid):
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to {pid}")
    except Exception as e:
        print(f"Error killing {pid}: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        kill_process(int(sys.argv[1]))
