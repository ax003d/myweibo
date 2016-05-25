#!/bin/bash

/usr/bin/printenv | grep -v affinity | grep -v LESSCLOSE > /app/.env
cron -f
