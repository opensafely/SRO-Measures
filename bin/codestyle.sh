#!/usr/bin/env bash

echo 'Running black...'
black --line-length 79 "$@"
echo '...done'

echo 'Running flake8...'
flake8 "$@"
echo '...done'

echo 'Running isort...'
isort "$@"
echo '...done'
