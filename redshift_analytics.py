"""
Redshift Analytics Engine
Author: Sumanth Battu
Description: Optimized Redshift queries and analytics
             for financial data warehousing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedshiftAnalytics:
    """
    Redshift-optimized analytics engine for financial data.
    Demonstrates table optimization, KPI reporting,
    and statistical analysis for BIE roles.
    """

    def __init__(self, connection_config: dict = None):
        self.config = connection_config or {}
        self.query_log = []
        logger.info("RedshiftAnalytics initialized")

    def optimize_table_ddl(self, table_name: str) -> str:
        """
        Generate optimized Redshift table DDL
        with distribution and sort keys
        """
        ddl = f"""
-- Optimized Redshift table for {table_name}
-- Distribution key: customer_id (even distribution)
-- Sort key: transaction_date (range scan optimization)
CREATE TABLE IF NOT EXISTS {table_name} (
    transaction_id      BIGINT          NOT NULL,
    customer_id         INTEGER         NOT NULL,
    amount              DECIMAL(12, 2)  NOT NULL,
    transaction_date    TIMESTAMP       NOT NULL,
    category            VARCHAR(50)     NOT NULL,
    status              VARCHAR(20)     NOT NULL,
    customer_segment    VARCHAR(20),
    amount_bucket       VARCHAR(20),
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
)
DISTSTYLE KEY
DISTKEY (customer_id)
SORTKEY (transaction_date, customer_id)
ENCODE AUTO;

-- Create materialized view for dashboard performance
CREATE MATERIALIZED VIEW mv_{table_name}_daily AS
SELECT
    DATE_TRUNC('day', transaction_date)     AS report_date,
    COUNT(DISTINCT customer_id)             AS unique_customers,
    COUNT(transaction_id)                   AS total_transactions,
    SUM(amount)                             AS total_revenue,
    AVG(amount)                             AS avg_transaction
FROM {table_name}
WHERE status = 'completed'
GROUP BY DATE_TRUNC('day', transaction_date);
        """.strip()

        logger.info(f"Generated optimized DDL for {table_name}")
        return ddl

    def executive_kpi_report(self,
                             df: pd.DataFrame,
                             period: str = 'monthly') -> pd.DataFrame:
        """
        Generate executive KPI report
        Reliable, accurate, timely reporting for leadership
        """
        logger.info(f"Generating {period} KPI report...")

        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

        if period == 'daily':
            df['period'] = df['transaction_date'].dt.date
        elif period == 'weekly':
            df['period'] = df['transaction_date'].dt.to_period('W')
        else:
            df['period'] = df['transaction_date'].dt.to_period('M')

        kpi_report = df[df['status'] == 'completed'].groupby(
            'period'
        ).agg(
            total_revenue=('amount', 'sum'),
            unique_customers=('customer_id', 'nunique'),
            total_transactions=('transaction_id', 'count'),
            avg_transaction=('amount', 'mean'),
            max_transaction=('amount', 'max'),
            min_transaction=('amount', 'min')
        ).round(2).reset_index()

        # Add growth metrics
        kpi_report['revenue_growth_pct'] = (
            kpi_report['total_revenue'].pct_change() * 100
        ).round(2)
        kpi_report['customer_growth_pct'] = (
            kpi_report['unique_customers'].pct_change() * 100
        ).round(2)

        logger.info(
            f"KPI report generated: {len(kpi_report)} periods"
        )
        return kpi_report

    def statistical_analysis(self,
                             df: pd.DataFrame) -> dict:
        """
        Statistical analysis to uncover hidden
        patterns, trends and opportunities
        """
        logger.info("Running statistical analysis...")

        completed = df[df['status'] == 'completed']['amount']

        # Descriptive statistics
        stats = {
            'mean': completed.mean(),
            'median': completed.median(),
            'std': completed.std(),
            'variance': completed.var(),
            'skewness': completed.skew(),
            'kurtosis': completed.kurtosis(),
            'percentile_25': completed.quantile
