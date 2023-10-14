import bittensor as bt
import argparse
import os

ss58HotKey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
ss58ColdKey = "5Ct64HXTt77uibdNGeFPrezG9iQ3Ut12ZyQj4g2KSBrXrBCE"


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


def main():
    config = get_config()
    bt.logging(config=config, logging_dir=config.full_path)

    sub = bt.subtensor()
    bt.logging.info("Starting subtensor connector")
    valis = bt.subtensor.max_allowed_validators(sub, netuid=3)
    stake = bt.subtensor.get_total_stake_for_hotkey(sub, ss58_address=ss58HotKey)
    keyStake = bt.subtensor.get_stake_for_coldkey_and_hotkey(sub, hotkey_ss58=ss58HotKey,coldkey_ss58=ss58ColdKey).tao
    bt.logging.debug(f"Number of allowed validators: {valis}, stake (total): {stake}, {keyStake}")
    # delegates = bt.subtensor.get_delegates(sub)


# print(delegates)


def testing():
    myList = [96, 128, 85, 137, 89, 98, 4, 126, 3, 17, 147, 146, 63, 139, 141, 15, 75, 123, 23, 2, 5, 54, 53, 52, 10]
    print(myList)
    if 100 in myList:
        print("UID 100 was in the list")
    else:
        print("UID 100 was not in the list, adding")
        myList[0] = 100
    print(myList)


if __name__ == "__main__":
    main()
