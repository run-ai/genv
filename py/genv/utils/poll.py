import errno
import os
import subprocess


def poll_pid(pid: int) -> bool:
    """
    Kill the process of the given pid.
    :param pid: pid of the process to kill
    :return: True iff the process has been killed successfully.
    """
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        elif e.errno == errno.EPERM:
            return True
        else:
            raise
    else:
        return True


def poll_jupyter_kernel(kernel_id: str) -> bool:
    # TODO(raz): what about the case when 'jupyter' is not available in the
    #            environment that we are currently running in?
    #
    # should we ignore such cases and _not_ cleanup kernels if we don't have the 'jupyter' command?
    # should we look for kernel processes similarly to 'ps -ef | grep kernel-'?
    # should we document the kernel json path when activating a kernel, so that the path will
    # be known in other environments as well? what if we don't have read permissions?

    result = subprocess.run(
        ["sh", "-c", f"ls $(jupyter --runtime-dir)/kernel-{kernel_id}.json"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0
