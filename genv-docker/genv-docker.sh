#!/bin/bash

GENV_DOCKER=${GENV_DOCKER:-"docker"}

program="${0##*/}"

print_error_and_exit()
{
    echo "$program: [ERROR]: $1" 1>&2
    exit 1
}

print_run_usage()
{
    echo "Genv Usage: genv-docker run [OPTIONS] ..."
    echo
    echo "Options:"
    echo "  --gpus          Configure the environment device count and attach devices using Genv"
    echo "  --gpu-memory    Configure the environment memory capacity (e.g. 3g, 42mi, 44040192)"
    echo "                    b - bytes (default)"
    echo "                    k - kilobytes, ki - kibibytes"
    echo "                    m - megabytes, mi - mebibytes"
    echo "                    g - gigabytes, gi - gibibytes"
    echo
    echo "Extra Options:"
    echo "  --help          Show this help message and exit"
    echo "  --dry-run       Show the raw 'docker' command without actually executing it"
    echo
}

args_before=()
args_middle=()
args_after=()

while [[ $# -gt 0 ]] ; do
    arg=$1
    shift

    if [[ $args_command = "run" ]] ; then
        if [[ $arg = "--gpus" ]] ; then
            gpus=$1
            shift

            re='^[0-9]+$'
            if ! [[ $gpus =~ $re ]] ; then
                print_error_and_exit "Invalid value for '--gpus' ($gpus)"
            fi
        elif [[ $arg = "--gpu-memory" ]] ; then
            gpu_memory=$1
            shift

            re='^[0-9]+(b|k|ki|m|mi|g|gi)?$'
            if ! [[ $gpu_memory =~ $re ]] ; then
                print_error_and_exit "Invalid value for '--gpu-memory' ($gpu_memory)"
            fi
        elif [[ $arg = "--dry-run" ]] ; then
            dry_run="1"
        else
            if [[ $arg = "--help" ]] ; then
                # here we print the help message of genv-docker and then pass to the `docker` command
                # so both help messages will be printed.
                print_run_usage
            elif [[ "$arg" == *" "* ]]; then
                # arguments can be passed with quotes. we need to preserve the quotes but $arg is
                # without them. currently we manually wrap arguments of more than a single word
                # with quotes. this is to support the commands like the following:
                #
                #   genv-docker run -it --rm ubuntu bash -c "echo hello"

                arg="\"$arg\""
            fi

            args_after+=($arg)
        fi
    else
        args_before+=($arg)

        if [[ $arg = "run" ]] ; then
            args_command=$arg
        fi
    fi
done

if [[ $args_command = "run" ]] ; then
    args_middle+=("--runtime=genv")

    if [[ "$gpus" != "" ]]; then
        args_middle+=("-e GENV_GPUS=$gpus")
    fi

    if [[ "$gpu_memory" != "" ]]; then
        args_middle+=("-e GENV_GPU_MEMORY=$gpu_memory")
    fi
fi

command="$GENV_DOCKER ${args_before[@]} ${args_middle[@]} ${args_after[@]}"

if [[ $dry_run = "1" ]] ; then
    echo $command
else
    eval $command
fi
