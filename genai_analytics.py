"""
GenAI Self-Service Analytics Tool
Author: Sumanth Battu
Description: LLM-integrated natural language query interface
             for self-service business intelligence
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenAIAnalytics:
    """
    GenAI-powered self-service analytics tool.
    Converts natural language questions into SQL queries
    and delivers actionable business insights.
    Directly mirrors Amazon Key's GenAI analytics requirement.
    """

    def __init__(self, schema: dict):
        self.schema = schema
        self.query_history = []
        self.insights_cache = {}
        logger.info("GenAI Analytics tool initialized")

    def parse_business_question(self, question: str) -> dict:
        """
        Parse natural language business question
        into structured query components
        """
        logger.info(f"Parsing question: {question}")

        # Identify metrics requested
        metrics = []
        if any(word in question.lower() for word in
               ['revenue', 'sales', 'amount']):
            metrics.append('SUM(amount) as total_revenue')
        if any(word in question.lower() for word in
               ['customer', 'user']):
            metrics.append('COUNT(DISTINCT customer_id) as customers')
        if any(word in question.lower() for word in
               ['transaction', 'order']):
            metrics.append('COUNT(transaction_id) as transactions')
        if any(word in question.lower() for word in
               ['average', 'avg']):
            metrics.append('AVG(amount) as avg_value')

        # Identify time dimension
        time_dimension = None
        if 'daily' in question.lower() or 'day' in question.lower():
            time_dimension = "DATE_TRUNC('day', transaction_date)"
        elif 'monthly' in question.lower() or 'month' in question.lower():
            time_dimension = "DATE_TRUNC('month', transaction_date)"
        elif 'weekly' in question.lower() or 'week' in question.lower():
            time_dimension = "DATE_TRUNC('week', transaction_date)"

        # Identify filters
        filters = []
        if 'completed' in question.lower():
            filters.append("status = 'completed'")
        if 'premium' in question.lower():
            filters.append("customer_segment = 'Premium'")

        return {
            'metrics': metrics if metrics else ['COUNT(*) as count'],
            'time_dimension': time_dimension,
            'filters': filters,
            'original_question': question
        }

    def generate_sql(self, parsed_question: dict) -> str:
        """
        Generate SQL query from parsed question components
        """
        metrics = ', '.join(parsed_question['metrics'])
        where_clause = ''
        group_clause = ''
        order_clause = ''

        if parsed_question['filters']:
            where_clause = 'WHERE ' + ' AND '.join(
                parsed_question['filters']
            )

        if parsed_question['time_dimension']:
            metrics = (
                f"{parsed_question['time_dimension']} as period, "
                + metrics
            )
            group_clause = (
                f"GROUP BY {parsed_question['time_dimension']}"
            )
            order_clause = (
                f"ORDER BY {parsed_question['time_dimension']} DESC"
            )

        sql = f"""
SELECT
    {metrics}
FROM financial_transactions
{where_clause}
{group_clause}
{order_clause}
LIMIT 100;
        """.strip()

        logger.info(f"Generated SQL query")
        return sql

    def execute_and_analyze(self,
                            df: pd.DataFrame,
                            question: str) -> dict:
        """
        Execute analysis and generate insights
        from natural language question
        """
        logger.info(f"Analyzing: {question}")
        parsed = self.parse_business_question(question)
        sql = self.generate_sql(parsed)

        # Simulate query execution on dataframe
        result = self._simulate_query(df, parsed)

        # Generate insights
        insights = self._generate_insights(result, question)

        # Log to history
        self.query_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'sql': sql,
            'rows_returned': len(result)
        })

        return {
            'question': question,
            'sql_generated': sql,
            'results': result.to_dict('records')[:5],
            'insights': insights,
            'rows_returned': len(result)
        }

    def _simulate_query(self,
                        df: pd.DataFrame,
                        parsed: dict) -> pd.DataFrame:
        """Simulate SQL query execution"""
        result = df.copy()

        # Apply filters
        if 'completed' in str(parsed['filters']):
            result = result[result['status'] == 'completed']

        # Apply aggregations
        if parsed['time_dimension']:
            result['period'] = pd.to_datetime(
                result['transaction_date']
            ).dt.to_period('M')
            result = result.groupby('period').agg(
                total_revenue=('amount', 'sum'),
                customers=('customer_id', 'nunique'),
                transactions=('transaction_id', 'count')
            ).reset_index()
        else:
            result = pd.DataFrame([{
                'total_revenue': result['a
