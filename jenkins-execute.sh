#!/bin/bash

python bootstrap.py
bin/buildout -c jenkins.cfg
bin/jenkins-test
bin/jenkins-test-coverage
