# let
#   pkgs = import <nixpkgs> {};
# in pkgs.mkShell {
#   packages = [
#     pkgs.sage
#     (pkgs.python313.withPackages (python-pkgs: [
#       python-pkgs.jupyterlab
#     ]))
#   ];
# }
{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python313Packages }:

let
  kernels = with pythonPackages; [
    pkgs.sage
  ];

in pkgs.mkShell {
  buildInputs = with pythonPackages; [
    jupyterlab
    # numpy
    # matplotlib
  ] ++ kernels;

  shellHook = ''
    # kernels
    # export JUPYTER_PATH="${pkgs.lib.concatMapStringsSep ":" (p: "${p}/share/jupyter/") kernels}"
    # Add sage jupyter kernel by running first few lines of setup for sage
    source <(head -n 8 $(which sage))
    jupyter kernelspec install --user $JUPYTER_PATH/kernels/sagemath

    alias start="jupyter lab"
  '';
}
