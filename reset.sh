#!/usr/bin/env bash
rm happyteams/db.sqlite3
rm -rf happyteams/crm/migrations/
rm -rf happyteams/planning/migrations/
rm -rf happyteams/resources/migrations/
python happyteams/manage.py makemigrations crm planning resources
python happyteams/manage.py migrate
python happyteams/manage.py create_fixture_data_for_planning
python happyteams/manage.py create_fixture_data_for_resources
python happyteams/manage.py create_fixture_data_for_crm
python happyteams/manage.py populate_skill_enjoyment_levels