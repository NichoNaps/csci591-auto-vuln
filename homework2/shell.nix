{ pkgs ? import <nixpkgs> {} }:

# Nixos had too new of a version of gcc 
# at the time of the project so it could not run voidsmtpd.
# This script generates a environement with a downgraded gcc
# to work around this.
(pkgs.buildFHSEnv {
    name = "environment";
    targetPkgs = pkgs: (with pkgs; [
    gcc11

    busybox # for telnet

  ]);
  multiPkgs = pkgs: (with pkgs; [
    gcc11
  ]);
  
  runScript = ''

    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
          pkgs.gcc11Stdenv.cc.cc.lib
        ]}";

  bash'';


}).env
