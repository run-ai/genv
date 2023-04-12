#!/bin/bash

GENV_DOCKER=${GENV_DOCKER:-"docker"}

program="${0##*/}"

print_error_and_exit()
{
    echo "$program: [ERROR]: $1" 1>&2
    exit 1
}

# default arguments
activate="1"
attach="1"
shims="1"

print_run_usage()
{
    echo "Genv Usage: genv-docker run ..."
    echo
    echo "Configuration:"
    echo "  --gpus          Configure the environment device count"
    echo "  --gpu-memory    Configure the environment memory capacity (e.g. 3g, 42mi, 44040192)"
    echo "                    b - bytes (default)"
    echo "                    k - kilobytes    ki - kibibytes"
    echo "                    m - megabytes    mi - mebibytes"
    echo "                    g - gigabytes    gi - gibibytes"
    echo "  --eid           Configure the environment identifier"
    echo
    echo "Options:"
    echo "  --[no-]activate     Activate environment for the container; default: $activate"
    echo "  --[no-]attach       Attach devices to the environment; default: $attach"
    echo "  --[no-]shims        Mount shims to the container; default: $shims"
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
        # configuration
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
        elif [ $arg = "--eid" ] ; then eid=$1 ; shift

        # options
        elif [ $arg = "--activate" ] ; then activate="1" ; elif [ $arg = "--no-activate" ] ; then activate="0"
        elif [ $arg = "--attach" ] ; then attach="1" ; elif [ $arg = "--no-attach" ] ; then attach="0"
        elif [ $arg = "--shims" ] ; then shims="1" ; elif [ $arg = "--no-shims" ] ; then shims="0"

        # extra options
        elif [[ $arg = "--dry-run" ]] ; then dry_run="1"
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

    # configuration
    if [[ "$gpus" != "" ]]; then
        # TODO(raz): support explicit specification of devices and not only attaching using Genv
        args_middle+=("-e GENV_GPUS=$gpus")
    fi

    if [[ "$gpu_memory" != "" ]]; then
        args_middle+=("-e GENV_GPU_MEMORY=$gpu_memory")
    fi

    if [ -n "$eid" ]; then
        args_middle+=("-e GENV_ENVIRONMENT_ID=$eid")
    fi

    # options
    if [ "$activate" = "0" ]; then
        args_middle+=("-e GENV_ACTIVATE=0")
    fi

    if [ "$attach" = "0" ]; then
        args_middle+=("-e GENV_ATTACH=0")
    fi

    if [ "$shims" = "0" ]; then
        args_middle+=("-e GENV_MOUNT_SHIMS=0")
    fi
fi

command="$GENV_DOCKER ${args_before[@]} ${args_middle[@]} ${args_after[@]}"

if [[ $dry_run = "1" ]] ; then
    echo $command
else
    eval $command
fi
