# let
#   pkgs = import <nixpkgs> {};
# in pkgs.mkShell {
#   packages = [
    # pkgs.sage
#   ];
#
#   shellHook = ''
#     fish -C "source .venv/bin/activate.fish"
#   '';
# }
# { pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python313Packages }:
#
# let
#   kernels = with pythonPackages; [
#     pkgs.sage
#   ];
#
# in pkgs.mkShell {
#   buildInputs = with pythonPackages; [
#     jupyterlab
#     # numpy
#     # matplotlib
#   ] ++ kernels;
#
#   shellHook = ''
#     # kernels
#     # export JUPYTER_PATH="${pkgs.lib.concatMapStringsSep ":" (p: "${p}/share/jupyter/") kernels}"
#     # Add sage jupyter kernel by running first few lines of setup for sage
#     source <(head -n 8 $(which sage))
#     jupyter kernelspec install --user $JUPYTER_PATH/kernels/sagemath
#
#     alias start="jupyter lab"
#   '';
# }

{ pkgs ? import <nixpkgs> {} }:
let lib-path = with pkgs; lib.makeLibraryPath [
    libffi
    openssl
    stdenv.cc.cc
  ];
  kernels = [
        pkgs.sage
    ];
in
(pkgs.mkShell {
  packages = [
    pkgs.sage
  ];
  buildInputs = with pkgs; [
    python313
    python313Packages.pip
    python313Packages.virtualenv
  ];
  shellHook = ''
      # kernels
      export JUPYTER_PATH="${pkgs.lib.concatMapStringsSep ":" (p: "${p}/share/jupyter/") kernels}"
      # Add sage jupyter kernel by running first few lines of setup for sage
      source <(head -n 8 $(which sage))
      jupyter kernelspec install --user $JUPYTER_PATH/kernels/sagemath
      fish -C "source .venv/bin/activate.fish"; exit
    '';
  env = {
      LD_LIBRARY_PATH="${lib-path}";
    };
})
