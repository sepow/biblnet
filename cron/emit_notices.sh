WORKON_HOME=/home/sepow/webapps/devdjango
PROJECT_ROOT=/home/sepow/webapps/devdjango/pinax-env/biblnet

# activate virtual environment
source $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py emit_notices >> $PROJECT_ROOT/logs/cron_mail.log 2>&1
