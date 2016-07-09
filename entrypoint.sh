#!/bin/bash

/usr/bin/printenv | grep -v affinity | grep -v LESSCLOSE > /app/.env
/usr/bin/supervisord -n

