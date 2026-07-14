#!/bin/bash
ssh -i ~/.ssh/proxmox_tds root@100.99.198.22 "pct exec 101 -- hostname -I"
