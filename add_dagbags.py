import os
from airflow.models import DagBag
dags_dirs = ['/home/brig/airflow/new_dag_bag1', '/home/brig/airflow/new_dag_bag2']

for dir in dags_dirs:
   dag_bag = DagBag(os.path.expanduser(dir))

   if dag_bag:
      for dag_id, dag in dag_bag.dags.items():
         globals()[dag_id] = dag
