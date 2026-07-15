from django.core.management.base import BaseCommand
from complaints.sla_engine import run_sla_engine


class Command(BaseCommand):
    help = "Runs SLA automation engine"

    def handle(self, *args, **kwargs):
        self.stdout.write("Running SLA Engine...")

        run_sla_engine()

        self.stdout.write(self.style.SUCCESS("SLA Engine Completed"))