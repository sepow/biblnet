WORKON_HOME=/home/biblnet/webapps/bnet
PROJECT_ROOT=/home/biblnet/webapps/bnet/pinax-env/biblnet

# activate virtual environment
source /home/biblnet/webapps/bnet/pinax-env/bin/activate

cd /home/biblnet/webapps/bnet/pinax-env/biblnet
python manage.py send_mail >> /home/biblnet/webapps/bnet/pinax-env/biblnet/logs/cron_mail.log 2>&1
