#!/bin/bash

/usr/bin/printenv | grep -v affinity | grep -v LESSCLOSE > /app/gizwits_site/.env
cron -f
