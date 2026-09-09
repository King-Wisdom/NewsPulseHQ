import os
import sys

from django.apps import AppConfig
from django.conf import settings


# Management commands that should never trigger the background
# scheduler (short-lived commands, or the import itself).
EXCLUDED_MANAGEMENT_COMMANDS = {
    "makemigrations",
    "migrate",
    "collectstatic",
    "test",
    "shell",
    "shell_plus",
    "dbshell",
    "createsuperuser",
    "loaddata",
    "dumpdata",
    "import_news",
    "check",
}


class NewspulsehqappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newspulsehqapp"

    def ready(self):
        if not getattr(settings, "ENABLE_NEWS_SCHEDULER", True):
            return

        argv = sys.argv

        if len(argv) > 1 and argv[1] in EXCLUDED_MANAGEMENT_COMMANDS:
            return

        # With the dev-server autoreloader, apps are loaded twice: once in
        # the watcher process and once in the reloaded child (RUN_MAIN=true).
        # Only start the scheduler in the process that actually serves requests.
        if "runserver" in argv and os.environ.get("RUN_MAIN") != "true":
            return

        from . import scheduler

        scheduler.start()
