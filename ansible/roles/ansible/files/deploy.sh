#!/bin/bash

/usr/bin/ansible-playbook \
  --vault-password-file="/home/pi/vault"  \
  --inventory-file="/home/github/ansible/inventory" \
  "/home/github/ansible/setup.yml"
