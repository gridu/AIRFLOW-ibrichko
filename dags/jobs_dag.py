from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
#rom airflow.operators.postgres_custom import PostgreSQLCountRowsOperator
from airflow.hooks.postgres_hook import PostgresHook
from uuid import uuid4
from time import time




def start_dag(dag_id, database):
    def init():
        print(f"{dag_id} start processing tables in DB: {database}")

    return init


def check_table_exist(schema, table):
    def init():
        hook = PostgresHook()
        query = '''
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = %s
                          AND table_name = %s
        '''
        is_exist = hook.get_first(sql=query, parameters=(schema, table))

        return ['do_nothing' if is_exist else 'create_table']

    return init


def create_table_func(schema, table):
    def init():
        hook = PostgresHook()
        create_table_query = f'''
                CREATE TABLE {schema}.{table}(
                   id uuid NOT NULL,
                   "user" VARCHAR (50) NOT NULL,
                   timestamp TIMESTAMP NOT NULL
                )
        '''
        hook.run(sql=f'CREATE SCHEMA IF NOT EXISTS {schema}', autocommit=True)
        hook.run(sql=create_table_query, autocommit=True)

    return init


def insert_row(schema, table):
    def init(**context):
        user = context['ti'].xcom_pull(task_ids='who_am_i')
        hook = PostgresHook()
        query = f'''
           INSERT INTO {schema}.{table} 
           VALUES (%s, %s, to_timestamp(%s))
        '''
        hook.run(sql=query,
                 parameters=(uuid4(), user, time()),
                 autocommit=True)

    return init


def create_dag(dag_id, start_date, table, database, schedule_interval=None):
    with DAG(
            dag_id=dag_id,
            start_date=start_date,
            schedule_interval=schedule_interval
    ) as dag:
        start = PythonOperator(task_id='start', python_callable=start_dag(dag_id, database))

        who_am_i = BashOperator(task_id='who_am_i', xcom_push=True, bash_command='whoami')

        check_exist = BranchPythonOperator(task_id="check_table_exist",
                                           python_callable=check_table_exist(schema=database, table=table))

        create_table = PythonOperator(task_id='create_table',
                                      python_callable=create_table_func(schema=database, table=table))

        do_nothing = DummyOperator(task_id='do_nothing')

        insert_new_row = PythonOperator(task_id='insert_new_row', provide_context=True, trigger_rule='all_done',
                                        python_callable=insert_row(schema=database, table=table))

        query_the_table = PostgreSQLCountRows(task_id='query_the_table', schema=database, table=table)

        end = BashOperator(task_id='end', xcom_push=True, bash_command="echo '{{ run_id }} ended'")

    start >> who_am_i >> check_exist >> [create_table, do_nothing] >> insert_new_row >> end

    return dag



config = {
   'brig_1': {'schedule_interval':"@hourly", "start_date": datetime(2020, 3, 30),"table_name": "table_brig_1"},
   'brig_2': {'schedule_interval':"*/15 * * * ", "start_date": datetime(2020, 3, 30),"table_name": "table_brig_2"},
   'brig_3':{'schedule_interval': "*/10 * * * ", "start_date": datetime(2020, 3, 30),"table_name": "table_brig_3"}}




for key, value in config.items():
    globals()[key] = create_dag(dag_id=key,
                                start_date=value['start_date'],
                                schedule_interval=value['schedule_interval'],
                                table=value['table_name'],
                                database='airflow')





