import json
import logging

from environs import Env

env = Env()
env.read_env()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Config:
    TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
    PROVIDER_URL = env.str("PROVIDER_URL")
    CONTRACT_ADDRESS_HASH = env.str("CONTRACT_ADDRESS_HASH")
    DISTRIBUTOR_WALLET_ADDRESS = env.str("DISTRIBUTOR_WALLET_ADDRESS")

    REPORT_PERIOD_SEC = env.int("REPORT_PERIOD_SEC", 3600 * 24)
    REPORT_SEND_INTERVAL_SEC = env.int("REPORT_SEND_INTERVAL_SEC", 3600 * 4)

    try:
        with open("contract_abi.json") as file:
            CONRACT_ABI = json.load(file)
    except FileNotFoundError as e:
        logging.error(f"Failed to load contract abi. Details: {e}")

    DB_USER = env.str("DB_USER")
    DB_PASSWORD = env.str("DB_PASSWORD")
    DB_HOST = env.str("DB_HOST")
    DB_PORT = env.str("DB_PORT")
    DB_NAME = env.str("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    REPORT_RECIEVER_CHAT_ID = env.str("REPORT_RECIEVER_CHAT_ID")
