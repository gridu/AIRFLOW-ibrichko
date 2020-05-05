import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook

log = logging.getLogger(__name__)


class PostgreSQLCountRows(BaseOperator):
    @apply_defaults
    def __init__(self, table, *args, **kwargs):
        self.table = table
        self.hook = PostgresHook()
        super(PostgreSQLCountRows, self).__init__(*args, **kwargs)

    def execute(self, context):
        result = self.hook.get_first(sql=f"SELECT COUNT(*) FROM {self.table_name};")
        log.info(f"result: {result}")
        return result


class PostgreSQLCustomPlugin(AirflowPlugin):
    name = "postgres_custom"
    operators = [PostgreSQLCountRows]
