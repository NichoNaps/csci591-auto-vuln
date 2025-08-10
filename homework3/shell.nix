# This script is a work around for nixos to get z3 to work.
let
  pkgs = import <nixpkgs> { };
  # unstable = import <nixos-unstable> { config = { allowUnfree = true; }; };
in
pkgs.mkShell rec {

  buildInputs = with pkgs; [
    gcc
    libgcc
    # tk
    graphviz
  ];

  shellHook = ''
    source env/bin/activate
    echo "activating python virt env...."

    # this is needed to make z3 happy
    export LD_LIBRARY_PATH=${pkgs.libgcc.lib}/lib:$LD_LIBRARY_PATH
  '';
}
