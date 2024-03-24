from datetime import datetime
from decimal import Decimal


class ReportBuilder:
    def build_report(self, report_data: dict) -> str:
        input_aix = self._extract_token_parameter_value(report_data, "total_input_aix")
        distributed_aix = self._extract_token_parameter_value(report_data, "total_distributed_aix")
        swapped_eth = self._extract_token_parameter_value(report_data, "total_swapped_eth")
        distributed_eth = self._extract_token_parameter_value(report_data, "total_distributed_eth")

        distributor_balance = self._extract_token_parameter_value(report_data, "distributor_balance")
        distributor_wallet_address = report_data.get("distributor_wallet_address")

        start_date = report_data.get("start_date")
        firtx_tx_ago = self._get_time_ago_string(start_date)

        end_date = report_data.get("end_date")
        last_tx_ago = self._get_time_ago_string(end_date)

        report = f"""
        Daily $AIX Stats:
            - First TX: {firtx_tx_ago}
            - Last TX: {last_tx_ago}
            - AIX processed: {input_aix}
            - AIX distributed: {distributed_aix}
            - ETH bought: {swapped_eth}
            - ETH distributed: {distributed_eth}

            Distributor wallet: {distributor_wallet_address}
            Distributor balance: {distributor_balance} ETH
            """

        return report

    def _extract_token_parameter_value(self, report_data: dict, param_name: str) -> float:
        wei_parameter_value = report_data.get(param_name, 0)
        return self._convert_base_units_to_tokens(wei_parameter_value)

    @staticmethod
    def _convert_base_units_to_tokens(unit_value: int, decimals: int = 18) -> float:
        return round(Decimal(unit_value) / (10**decimals), 2)

    @staticmethod
    def _get_time_ago_string(event_time: datetime) -> str:
        delta = datetime.utcnow() - event_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h{minutes}m ago"
