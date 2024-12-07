from paramiko.ssh_exception import NoValidConnectionsError
import contextlib
import fabric
import io
import json
import pytest
import requests
import time
import logging

logger = logging.getLogger(__name__)


with open("/run/secrets/ha-token", "r") as f:
    ha_token = f.read()


@contextlib.contextmanager
def disable_stdin_capture():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        yield monkeypatch


class BpiR4:
    def __init__(
        self,
        wan_ip: str,
        wan_ssh_port: int,
        homeassistant_url: str,
        switch_entity_id: str,
    ):
        self.wan_ip = wan_ip
        self.wan_ssh_port = wan_ssh_port
        self.homeassistant_url = homeassistant_url
        self.switch_entity_id = switch_entity_id

    def _hass_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json",
        }

    def set_power(self, active: bool):
        """Turn the AC power on or off."""
        data = {"entity_id": self.switch_entity_id}

        service = "turn_on" if active else "turn_off"

        url = f"{self.homeassistant_url}/api/services/switch/{service}"

        response = requests.post(url, headers=self._hass_headers(), json=data)
        response.raise_for_status()

    def power_on(self):
        logger.info("power_on")
        self.set_power(True)

    def power_off(self):
        logger.info("power_off")
        self.set_power(False)
        # power is not fully off until the capacitors in the power supply drain
        time.sleep(3)

    def shutdown_and_power_off(self):
        logger.info("Attempting clean shutdown")
        try:
            with disable_stdin_capture():
                self.ssh_with_timeout().run("shutdown -h 0")
        except (TimeoutError, NoValidConnectionsError):
            # assume powered off
            logger.warning("Failed to send shutdown command")
        else:
            # experimentally bpi takes ~5.91 seconds to cleanly shutdown
            # use safety factor of 2x, we want a clean shutdown if possible
            duration = 12
            logger.info(f"Waiting {duration} seconds for clean shutdown")
            time.sleep(duration)

        self.power_off()

    def ssh_with_timeout(self, timeout: int = 10):
        return fabric.Connection(
            host=self.wan_ip,
            port=self.wan_ssh_port,
            user="root",
            connect_timeout=timeout,
        )


@pytest.fixture
def bpi():
    with open("settings.json", "r") as f:
        settings = json.load(f)

    return BpiR4(
        wan_ip=settings["bpi_r4"]["wan_ip"],
        wan_ssh_port=settings["bpi_r4"]["wan_ssh_port"],
        homeassistant_url=settings["homeassistant"]["url"],
        switch_entity_id=settings["homeassistant"]["switch_entity_id"],
    )


def test_bootup(bpi: BpiR4):
    """
    The BPi-R4 has had problem with the mtk_soc module loading on bootup.

    This tests that the BPi-R4 can bootup without issue many times.
    """
    # experimentally BPi-R4 took 41.28 seconds to boot from an SD card
    # this will vary greatly with startup services and hardware
    # configuration
    boot_timeout = 90

    for i in range(0, 10):
        logger.info(f"Iteration: {i}")

        bpi.shutdown_and_power_off()

        bpi.power_on()
        with disable_stdin_capture():
            start_time = time.monotonic()
            while True:
                try:
                    bpi.ssh_with_timeout(timeout=boot_timeout).run(f"echo {i}")
                    break
                except NoValidConnectionsError as e:
                    # fabric may return NoValidConnectionsError before the timeout
                    # period has elapsed
                    elapsed = time.monotonic() - start_time
                    if elapsed >= boot_timeout:
                        raise e
                    logger.info(
                        f"{e}: {int(elapsed)}/{boot_timeout} seconds retrying..."
                    )
