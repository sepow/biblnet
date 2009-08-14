WORKON_HOME=/home/biblnet/webapps/bnet
PROJECT_ROOT=/home/biblnet/webapps/bnet/pinax-env/biblnet

# activate virtual environment
source $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py retry_deferred >> $PROJECT_ROOT/logs/cron_mail.log 2>&1
