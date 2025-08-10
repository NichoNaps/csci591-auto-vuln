let
  pkgs = import <nixpkgs> { };
  # unstable = import <nixos-unstable> { config = { allowUnfree = true; }; };
in
pkgs.mkShell rec {

  buildInputs = with pkgs; [
    gcc
    # openblas
    # blas

  ];

  shellHook = ''
    source env/bin/activate
    echo "activating python virt env...."
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
        # pkgs.openblas.dev
        pkgs.openblas
        pkgs.stdenv.cc.cc.lib # needed for numpy
        # pkgs.gcc.libc
        # pkgs.blas
        # -DBLAS_INCLUDE_DIRS="$env:RUNNER_TEMP/openblas/include" -DBLAS_LIBRARIES="$env:RUNNER_TEMP/openblas/lib/openblas.lib"
        ]}";
      

      # -DCPU_BASELINE=AVX -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DBLAS_INCLUDE_DIRS='/nix/store/7mfdligl170q59b6dg1ixikzsyymfcq1-openblas-0.3.27-dev/include'"  pip install llama-cpp-python --no-cache-dir --force-reinstall
      # add this line to the install command
      #echo '-DBLAS_INCLUDE_DIRS="${pkgs.openblas.dev}/include"'
    # pip install llama-cpp-python
  '';
}
