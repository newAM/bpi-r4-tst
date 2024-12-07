# BPi-R4 Test

Tests to debug and evaluate the BPi-R4.

My goal is to eventually deploy a BPi-R4 running NixOS as my home router.

Reference [nixos-sbc #12] for existing issues.

[nixos-sbc #12]: https://github.com/nakato/nixos-sbc/issues/12

## Running Tests

The test framework uses pytest, run `pytest` to execute tests.
Dependencies are managed with a [nix shell] that can be automatically loaded
with [direnv].

### Hardware

I use a switched PDU connected to home assistant to toggle AC power.
Use of other mechanisms will require modifications to the `BpiR4` fixture.

### Software

Please do not use production hardware for executing these tests.

Configure your Bananna Pi with an SSH server that allows root login with SSH
keys.

### Settings

Fill out the `settings.json` for your configuration.

```json
{
  "homeassistant": {
    "url": "https://my_home_assistant_url",
    "token_file": "/home/me/.secrets/my_token",
    "switch_entity_id": "switch.bpi_r4"
  },
  "bpi_r4": {
    "wan_ip": "10.1.2.3",
    "wan_ssh_port": 22
  }
}
```

[nix shell]: https://wiki.nixos.org/wiki/Development_environment_with_nix-shell
[direnv]: https://direnv.net
