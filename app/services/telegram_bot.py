import asyncio
import logging
from datetime import datetime, timedelta
from typing import NoReturn

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from app.definitions.enums import NearestDateDirection
from app.services.data_fetcher import DataFetcher
from app.services.database_manager import DatabaseManager
from app.services.report_builder import ReportBuilder

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
        self,
        token: str,
        database_manager: DatabaseManager,
        data_fetcher: DataFetcher,
        report_builder: ReportBuilder,
        report_period_sec: int,
        report_send_interval_sec: int,
        distributor_wallet_address: str,
        report_receiver_chat_id: str,
    ) -> None:
        self._application = ApplicationBuilder().token(token).build()

        self._job_queue = self._application.job_queue

        self._add_handlers()

        self._data_fetcher = data_fetcher
        self._report_builder = report_builder
        self._database_manager = database_manager
        self._report_period_sec = report_period_sec
        self._report_send_interval_sec = report_send_interval_sec
        self._distributor_wallet_address = distributor_wallet_address
        self._report_reciever_chat_id = report_receiver_chat_id

    def run(self) -> NoReturn:
        self._schedule_jobs()
        self._application.run_polling()

    def _schedule_jobs(self) -> None:
        self._job_queue.run_repeating(self._send_report_job, interval=self._report_send_interval_sec, first=1)

    async def _send_report_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self._send_report(context)

    async def _send_report(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        self._sync_distributions()

        report_content = await self._get_report_content()

        logging.info("Sending message to receiver chat...")
        await context.bot.send_message(chat_id=self._report_reciever_chat_id, text=report_content)

    def _add_handlers(self) -> None:
        start_handler = CommandHandler('start', self._start)
        self._application.add_handler(start_handler)

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self._sync_distributions()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hello! Thank you for launching!\n "
                 f"Since that moment I'm going to send a total distributions report to the chat "
                 f"with id {self._report_reciever_chat_id} every {self._report_send_interval_sec} seconds."
        )

    async def _get_report_content(self) -> str:
        logging.info("Extracting data from database...")
        report_data = self._get_report_data()

        logging.info("Building a report...")
        report_content = self._report_builder.build_report(report_data)

        return report_content

    def _sync_distributions(self) -> None:
        logging.info("Synchronizing distribution events with database...")
        last_event = self._database_manager.get_last_distribution_event()

        from_block = last_event.block_number if last_event else 0
        from_transaction_index = last_event.transaction_index if last_event else 0
        from_log_index = last_event.log_index + 1 if last_event else 0

        logging.info("Fetching distribution events from blockchain...")
        distribution_events = self._data_fetcher.fetch_distribution_events(from_block=from_block)

        logging.info("Adding distribution events to the database...")

        for event in distribution_events:
            event_unique_tuple = event.block_number, event.transaction_index, event.log_index
            if event_unique_tuple > (from_block, from_transaction_index, from_log_index):
                self._database_manager.add_distribution(event)

    def _get_report_data(self) -> dict:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(seconds=self._report_period_sec)
        total_distributions = self._database_manager.get_total_distributions(start_date, end_date)

        distributor_balance = self._data_fetcher.fetch_distributor_balance(self._distributor_wallet_address)

        return {
            "start_date": self._database_manager.get_nearest_distribution_date(start_date, NearestDateDirection.AFTER),
            "end_date": self._database_manager.get_nearest_distribution_date(end_date, NearestDateDirection.BEFORE),
            "distributor_balance": distributor_balance,
            "distributor_wallet_address": self._distributor_wallet_address,
            **total_distributions,
        }
