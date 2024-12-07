{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs,
  }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = [
        (pkgs.python3.withPackages (pypkg:
          with pypkg; [
            # test
            pytest
            fabric
            paramiko
            requests

            # lint
            flake8
            flake8-bugbear
            pep8-naming
          ]))
      ];
    };
  };
}
