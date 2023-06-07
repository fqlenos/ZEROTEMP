#!/bin/bash
set -e

sleep 2

IP=`tail -n 1 /etc/hosts | cut -f "1"`;
printf "ZEROTEMP listening on the selected port in: http://${IP}\n\n"
printf "'Ctrl + C' to stop server.\n\n"

cd /zerotemp/ && gunicorn --workers 4 --bind 0.0.0.0:5000 app.wsgi:app 2>/dev/null