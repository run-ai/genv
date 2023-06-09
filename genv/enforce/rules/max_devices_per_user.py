from genv.entities.enforce import Survey


def max_devices_per_user(*surveys: Survey, maximum: int) -> None:
    """
    Enforce maximum devices per user.
    """
    usernames = set(
        env.username
        for survey in surveys
        for env in survey.snapshot.envs
        if env.username
    )

    for username in usernames:
        snapshots = [survey.snapshot.filter(username=username) for survey in surveys]

        attached = sum(len(snapshot.devices) for snapshot in snapshots)

        if attached <= maximum:
            return

        over = attached - maximum

        if all(survey.hostname for survey in surveys):
            hosts = len([snapshot for snapshot in snapshots if len(snapshot.envs) > 0])

            print(
                f"User {username} is using {attached} devices on {hosts} hosts which is {over} more than the maximum allowed"
            )
        else:
            print(
                f"User {username} is using {attached} devices which is {over} more than the maximum allowed"
            )

        detached = 0

        for snapshot, survey in zip(snapshots, surveys):
            for device in snapshot.devices:
                if detached == over:
                    break  # already detached enough devices

                survey.detach(device.index, *device.eids)

                detached += 1
