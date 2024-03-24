import logging

from app.config import Config
from app.db.database import Base, engine
from app.services.data_fetcher import DataFetcher
from app.services.database_manager import DatabaseManager
from app.services.report_builder import ReportBuilder
from app.services.telegram_bot import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    database_manager = DatabaseManager()

    data_fetcher = DataFetcher(
        provider_url=Config.PROVIDER_URL,
        contract_address_hash=Config.CONTRACT_ADDRESS_HASH,
        contract_abi=Config.CONRACT_ABI,
        fetch_interval_sec=Config.REPORT_PERIOD_SEC,
    )

    report_builder = ReportBuilder()

    bot = TelegramBot(
        token=Config.TELEGRAM_BOT_TOKEN,
        database_manager=database_manager,
        data_fetcher=data_fetcher,
        report_builder=report_builder,
        report_period_sec=Config.REPORT_PERIOD_SEC,
        report_send_interval_sec=Config.REPORT_SEND_INTERVAL_SEC,
        distributor_wallet_address=Config.DISTRIBUTOR_WALLET_ADDRESS,
        report_receiver_chat_id=Config.REPORT_RECIEVER_CHAT_ID,
    )

    bot.run()
