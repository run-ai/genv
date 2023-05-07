from genv.entities.enforce import Survey


def non_env_processes(*surveys: Survey) -> None:
    """
    Terminates processes that are not running in environments.
    """
    for survey in surveys:
        for process in survey.snapshot.processes:
            if process.eid is not None:
                # TODO(raz): should we make sure that the environment actually exists in the snapshot?
                continue

            print(
                f"{f'[{survey.hostname}] ' if survey.hostname else ''}"
                f"Process {process.pid} is not running in a GPU environment"
            )

            survey.terminate(process.pid)
