from genv.entities.enforce import Survey


def env_devices(*surveys: Survey) -> None:
    """
    Terminates processes on devices not attached to their environments.
    """
    for survey in surveys:
        for env in survey.snapshot.envs:
            allowed = survey.snapshot.devices.filter(eid=env.eid).indices

            for process in survey.snapshot.processes.filter(eid=env.eid):
                unallowed = [index for index in process.indices if index not in allowed]

                if len(unallowed) == 0:
                    continue

                print(
                    f"{f'[{survey.hostname}] ' if survey.hostname else ''}"
                    f"Process {process.pid} from environment {env.eid} is using non-attached GPU(s) {','.join([str(index) for index in unallowed])}"
                )

                survey.terminate(process.pid)
