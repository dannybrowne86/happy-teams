rm happyteams/db.sqlite3
rm -rf happyteams/crm/migrations/
rm -rf happyteams/planning/migrations/
rm -rf happyteams/resources/migrations/
python happyteams/manage.py makemigrations crm planning resources
python happyteams/manage.py migrate
python happyteams/manage.py create_crm_fixture_data
