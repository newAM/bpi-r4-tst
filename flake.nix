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

            # lint and formatting
            ruff
          ]))
      ];
    };

    checks.x86_64-linux = {
      ruff_format = pkgs.runCommand "ruff_format" {} ''
        ${pkgs.ruff}/bin/ruff format --check ${self}
        touch $out
      '';

      ruff_check = pkgs.runCommand "ruff_check" {} ''
        ${pkgs.ruff}/bin/ruff check ${self}
        touch $out
      '';
    };
  };
}
