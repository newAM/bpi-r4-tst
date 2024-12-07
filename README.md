# BPi-R4 Test

Tests to debug and evaluate the BPi-R4.

My goal is to eventually deploy a BPi-R4 running NixOS as my home router.

Reference [nixos-sbc #12] for existing issues.

[nixos-sbc #12]: https://github.com/nakato/nixos-sbc/issues/12

## Running Tests

The test framework uses pytest, run `pytest` to execute tests.
Dependencies are managed with a [nix shell] that can be automatically loaded
with [direnv].

The tests are very specific to my hardware configuration and will likely
require modifications.
TODO: describe modifications.

[nix shell]: https://wiki.nixos.org/wiki/Development_environment_with_nix-shell
[direnv]: https://direnv.net
