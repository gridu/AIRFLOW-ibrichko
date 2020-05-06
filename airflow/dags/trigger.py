from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.models import Variable, TaskInstance
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.utils import dates
from airflow import DAG

run_file_path = Variable.get("RUN_FILE_PATH", default_var="/usr/local/shared/run.txt")
triggered_dag_id = Variable.get("TRIGGERED_DAG_ID", default_var="dag_id_1")


def process_results_subdag():
    def print_result_fn(*args, **kwargs):
        print(f"args = {args}")
        print(f"kwargs = {kwargs}")
        ti: TaskInstance = kwargs["ti"]
        result = ti.xcom_pull(task_ids="notify_completion", dag_id=triggered_dag_id, key="NOTIFY_COMPLETION")
        print(result)

    subdag = DAG(dag_id="trigger_dag.process_results", schedule_interval=None, start_date=dates.days_ago(2))
    with subdag:
        wait_for_triggered_dag = ExternalTaskSensor(
            task_id="wait_for_triggered_dag",
            external_dag_id=triggered_dag_id,
            external_task_id=None,
            poke_interval=5
        )
        print_result = PythonOperator(
            task_id="print_result",
            python_callable=print_result_fn,
            provide_context=True
        )
        remove_run_file = BashOperator(
            task_id="remove_run_file",
            bash_command=f"rm {run_file_path}"
        )
        create_timestamp_file = BashOperator(
            task_id="create_timestamp_file",
            bash_command="touch /usr/local/shared/{{ ts_nodash }} "
        )
        wait_for_triggered_dag >> print_result >> remove_run_file >> create_timestamp_file
    return subdag


dag = DAG(dag_id="trigger_dag", schedule_interval=None, start_date=dates.days_ago(2))
with dag:
    wait_for_run_file = FileSensor(
        task_id="wait_for_run_file",
        filepath=run_file_path,
        poke_interval=10
    )
    trigger_another_dag = TriggerDagRunOperator(
        task_id="trigger_another_dag",
        trigger_dag_id=triggered_dag_id,
        execution_date="{{ execution_date }}"
    )
    process_results = SubDagOperator(
        task_id="process_results",
        subdag=process_results_subdag()
    )
    wait_for_run_file >> trigger_another_dag >> process_results
