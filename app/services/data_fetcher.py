import logging
from datetime import datetime

from web3 import Web3

from app.db.models import DistributionEvent
from exceptions import Web3ConnectionError


class DataFetcher:
    def __init__(
        self, provider_url: str, contract_address_hash: str, contract_abi: dict, fetch_interval_sec: int
    ) -> None:
        self._web3 = Web3(Web3.HTTPProvider(provider_url))

        contract_address = Web3.to_checksum_address(contract_address_hash)
        self._contract = self._web3.eth.contract(address=contract_address, abi=contract_abi)

        self._fetch_interval_sec = fetch_interval_sec

        if not self._web3.is_connected():
            err_msg = "Failed to connect to blockchain"
            logging.error(err_msg)
            raise Web3ConnectionError(err_msg)

    def fetch_distribution_events(self, from_block: int) -> list[DistributionEvent]:
        events_dicts = self._contract.events.TotalDistribution.create_filter(
            fromBlock=from_block, toBlock='latest'
        ).get_all_entries()

        distributions_events: list[DistributionEvent] = []
        for event_dict in events_dicts:
            distribution_event = DistributionEvent(
                block_number=event_dict["blockNumber"],
                log_index=event_dict["logIndex"],
                transaction_index=event_dict["transactionIndex"],
                distributed_aix_amount=event_dict["args"]["distributedAixAmount"],
                distributed_eth_amount=event_dict["args"]["distributedEthAmount"],
                input_aix_amount=event_dict["args"]["inputAixAmount"],
                swapped_eth_amount=event_dict["args"]["swappedEthAmount"],
                occurred_at=datetime.utcfromtimestamp(self._web3.eth.get_block(event_dict["blockNumber"])["timestamp"]),
            )
            distributions_events.append(distribution_event)

        return distributions_events

    def fetch_distributor_balance(self, distributor_wallet_address: str) -> int:
        return self._web3.eth.get_balance(distributor_wallet_address)
