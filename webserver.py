import argparse
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import bittensor as bt
from bittensor import StakeInfo
from bittensor import subtensor

ss58HotKey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
ss58ColdKey = "5Ct64HXTt77uibdNGeFPrezG9iQ3Ut12ZyQj4g2KSBrXrBCE"
coldKeys = ["5Ct64HXTt77uibdNGeFPrezG9iQ3Ut12ZyQj4g2KSBrXrBCE", "5EP96q37SkwbFv8ef1XbdptHS4XFZ4eHq4rvAL9Jx2gjYudo"]
keys = {}


def get_config():
    parser = argparse.ArgumentParser()
    # Adds override arguments for network and netuid.
    parser.add_argument('--netuid', type=int, default=1, help="The chain subnet uid.")
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)
    # Parse the config (will take command-line arguments if provided)
    # To print help message, run python3 template/miner.py --help
    config = bt.config(parser)

    # Step 3: Set up logging directory
    # Logging is crucial for monitoring and debugging purposes.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'validator',
        )
    )
    # Ensure the logging directory exists.
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    # Return the parsed config.
    return config


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        bt.logging.debug(f"{self.client_address[0]} GET {self.path}")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        metrics: str = ""
        if len(keys) > 0:
            metrics += f"# HELP cold_hot_stake Cold key and hot key stake data\n# TYPE cold_hot_stake gauge\n"
            for ck in keys:
                for hk in keys[ck]:
                    metrics += f'cold_hot_stake{{coldkey="{ck}", hotkey="{hk}"}} {keys[ck][hk]}\n'

        self.wfile.write(bytes(metrics, 'utf-8'))
        return


def run():
    global keys
    while True:
        bt.logging.info("Updating data...")
        print(sub.substrate.get_block()['header']['number'])
        # valis = bt.subtensor.max_allowed_validators(sub, netuid=3)
        # stake = bt.subtensor.get_total_stake_for_hotkey(sub, ss58_address=ss58HotKey)
        bt.logging.debug(f"🥩 Fetching cold steak, key count: {len(coldKeys)}")
        whatsisthis = bt.subtensor.get_stake_info_for_coldkeys(sub, coldKeys)
        totalStake: float = 0.0
        for ck in whatsisthis:
            print(f"{ck}:")
            keys[ck] = {}
            sil: list[StakeInfo] = whatsisthis[ck]
            for si in sil:
                keys[ck][si.hotkey_ss58] = si.stake.tao
                print(f"\t{si.hotkey_ss58}:{si.stake.tao}")
                totalStake += si.stake.tao
            print(f"\tTotal staked: {totalStake}")
        # keyStake = bt.subtensor.get_stake_for_coldkey_and_hotkey(sub, hotkey_ss58=ss58HotKey, coldkey_ss58=ss58ColdKey).tao
        # bt.logging.debug(f"Number of allowed validators: {valis}, stake (total): {stake}, {keyStake}")
        # keys[ss58HotKey] = keyStake


if __name__ == '__main__':
    global sub
    config = get_config()
    bt.logging(config=config, logging_dir=config.full_path)
    bt.logging.trace(config)
    sub: subtensor = bt.subtensor()
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    web_thread = threading.Thread(name="webserver", target=server.serve_forever)
    web_thread.setDaemon = True
    run_thread = threading.Thread(name="main", target=run)

    web_thread.start()
    run_thread.start()
