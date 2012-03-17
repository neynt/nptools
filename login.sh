#!/bin/bash

curl -c kirls -d "username=$1&password=$2" http://www.neopets.com/login.phtml
