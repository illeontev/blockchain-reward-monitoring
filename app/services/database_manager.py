import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import Session
from app.db.models import DistributionEvent
from app.definitions.enums import NearestDateDirection


class DatabaseManager:
    @staticmethod
    def get_last_distribution_event() -> DistributionEvent:
        with Session() as session:
            last_event = (
                session.query(DistributionEvent)
                .order_by(
                    DistributionEvent.block_number.desc(),
                    DistributionEvent.transaction_index.desc(),
                    DistributionEvent.log_index.desc(),
                )
                .first()
            )
            return last_event

    @staticmethod
    def add_distribution(distribution_event: DistributionEvent) -> None:
        with Session() as session:
            try:
                session.add(distribution_event)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Failed to add record in the database: {e}")

    @staticmethod
    def get_total_distributions(start_date: datetime, end_date: datetime) -> dict:
        with Session() as session:
            aggregation = (
                session.query(
                    func.sum(DistributionEvent.distributed_aix_amount).label("total_distributed_aix"),
                    func.sum(DistributionEvent.distributed_eth_amount).label("total_distributed_eth"),
                    func.sum(DistributionEvent.input_aix_amount).label("total_input_aix"),
                    func.sum(DistributionEvent.swapped_eth_amount).label("total_swapped_eth"),
                )
                .filter(DistributionEvent.occurred_at.between(start_date, end_date))
                .one()
            )

            total_distributions = {
                "total_distributed_aix": aggregation.total_distributed_aix,
                "total_distributed_eth": aggregation.total_distributed_eth,
                "total_input_aix": aggregation.total_input_aix,
                "total_swapped_eth": aggregation.total_swapped_eth,
            }

            return total_distributions

    @staticmethod
    def get_nearest_distribution_date(target_date: datetime, direction: NearestDateDirection) -> Optional[datetime]:
        with Session() as session:
            query = session.query(DistributionEvent.occurred_at)

            if direction == NearestDateDirection.AFTER:
                event = (
                    query.filter(DistributionEvent.occurred_at >= target_date)
                    .order_by(DistributionEvent.occurred_at.asc())
                    .first()
                )
            elif direction == NearestDateDirection.BEFORE:
                event = (
                    query.filter(DistributionEvent.occurred_at <= target_date)
                    .order_by(DistributionEvent.occurred_at.desc())
                    .first()
                )
            else:
                raise ValueError("Invalid direction")

            return event.occurred_at if event else None
