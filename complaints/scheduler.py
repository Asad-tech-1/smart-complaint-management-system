from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from .sla_engine import run_sla_engine


def start():

    scheduler = BackgroundScheduler()

    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        run_sla_engine,
        "interval",
        minutes=5,
        id="run_sla_engine",
        replace_existing=True,
    )

    scheduler.start()

    print("SLA Scheduler Started...")