#!/bin/bash

set -e

GENV_SRC=${GENV_SRC:-"$HOME/genv"}
GENV_INSTALL_DEV_SHIMS=${GENV_INSTALL_DEV_SHIMS:-"1"}
GENV_INSTALL=${GENV_INSTALL:-"1"}

if ! [ -d "$GENV_SRC" ]; then
  echo "ERROR: Genv source directory not mounted properly"
  exit 1
fi

if [[ "$GENV_INSTALL_DEV_SHIMS" = "1" ]]; then
  devel_shims_path="$GENV_SRC/devel/shims"

  shopt -s nullglob

  for shim_path in "$devel_shims_path/"*; do
    shim="${shim_path##$devel_shims_path/}"

    if ! command -v $shim &> /dev/null
    then
      ln -s "$shim_path" "/usr/bin/$shim"
    fi
  done
fi

if [[ "$GENV_INSTALL" = "1" ]]; then
  pip install -e $GENV_SRC > /dev/null

  cat << EOT >> "$HOME/.bashrc"
eval "\$(genv shell --init)"
EOT
fi

( exec "$@" )
