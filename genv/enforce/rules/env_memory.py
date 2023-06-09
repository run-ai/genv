from genv.utils import memory_to_bytes, bytes_to_memory

from genv.entities.enforce import Survey


def env_memory(*surveys: Survey) -> None:
    """
    Terminates processes from environments that exceed their memory capacity.
    """
    for survey in surveys:
        for env in survey.snapshot.envs:
            if env.config.gpu_memory is None:
                continue

            for device in survey.snapshot.devices.filter(eid=env.eid):
                processes = survey.snapshot.processes.filter(
                    eid=env.eid, index=device.index
                )

                used_bytes = sum(process.total_bytes for process in processes)

                over_bytes = used_bytes - memory_to_bytes(env.config.gpu_memory)

                if not over_bytes > 0:
                    continue

                print(
                    f"{f'[{survey.hostname}] ' if survey.hostname else ''}"
                    f"Environment {env.eid} is using {bytes_to_memory(used_bytes, 'm')} on device {device.index} which is {bytes_to_memory(over_bytes, 'm')} over its capacity of {env.config.gpu_memory}"
                )

                freed_bytes = 0

                for process in processes:
                    survey.terminate(process.pid)

                    freed_bytes += process.total_bytes

                    if freed_bytes >= over_bytes:
                        break
