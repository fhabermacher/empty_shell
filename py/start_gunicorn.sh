#!/bin/bash
source /var/empty_shell/py/venv/bin/activate
export SAPO_TEST_DIR=/var/empty_shell
cd /var/empty_shell/py
gunicorn -w 4 --bind 0.0.0.0:8050 app:app.server
