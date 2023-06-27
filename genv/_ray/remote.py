import math
import os
import pynvml
import ray

import genv


def remote(**options):
    """Wraps a Ray remote function with a Genv environment.

    Inspired by https://github.com/ray-project/ray/blob/ray-2.5.1/python/ray/_private/worker.py#L3059
    """

    num_gpus = options.get("num_gpus", None)

    if num_gpus is None:
        raise ValueError(
            "The @genv.ray.remote decorator must be applied only when the argument 'num_gpus' is being used."
        )

    def _decorator(function):
        @ray.remote(**options)
        def _wrapper(*args, **kwargs):
            indices = ray.get_gpu_ids()

            config = genv.sdk.Env.Config(
                name=f"ray/{os.getpid()}", gpus=math.ceil(num_gpus)
            )

            if 0 < num_gpus < 1:
                if "GENV_MOCK_DEVICE_TOTAL_MEMORY" in os.environ:
                    total_bytes = genv.utils.memory_to_bytes(
                        os.environ["GENV_MOCK_DEVICE_TOTAL_MEMORY"]
                    )
                else:
                    index = indices[0]

                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    total_bytes = memory_info.total

                config.gpu_memory = str(math.floor(total_bytes * num_gpus))

            with genv.sdk.activate():
                genv.sdk.configure(config)

                # TODO(raz): support attaching to multiple indices at once
                for index in indices:
                    genv.sdk.attach(index=index, allow_over_subscription=True)

                return function(*args, **kwargs)

        return _wrapper

    return _decorator
