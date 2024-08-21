#!/bin/sh

branch_name=$(git symbolic-ref --short HEAD)

if [ "$branch_name" = "main" ]; then
  echo "Direct commits to the MAIN branch is RESTRICTED. Please create feature branch and raise PR"
  exit 1
fi