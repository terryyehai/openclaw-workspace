#!/bin/bash
# DDNS 更新腳本 - DuckDNS
# 每 5 分鐘檢查一次

DUCKDNS_TOKEN="0cabb390-b3a1-49b6-a72f-6561ad0b1919"
DOMAIN="terryclaw"

# 取得目前公網 IP
CURRENT_IP=$(curl -s ifconfig.me)

# 更新 DuckDNS
curl -s "https://www.duckdns.org/update?domains=$DOMAIN&token=$DUCKDNS_TOKEN&ip=$CURRENT_IP"

echo "IP: $CURRENT_IP"
