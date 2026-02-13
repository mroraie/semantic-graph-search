#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main() -> None:
    # Add the project root to sys.path so we can import 'src'
    import sys
    from pathlib import Path
    current_path = Path(__file__).resolve().parent.parent
    if str(current_path) not in sys.path:
        sys.path.append(str(current_path))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Install it with:\n"
            "    pip install django\n"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()


