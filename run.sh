#!/bin/sh

systemctl restart fastapi
sleep 2
curl -v --header "protection:YjWVsPQ6EM!WUaeSsydsPiWHDdp/vbg9JCNefGHltBdddPbb8md0mr=n86hzAyiv" "http://127.0.0.1:8000/v2/carlist/recent/"
