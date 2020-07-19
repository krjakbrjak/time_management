#!/usr/bin/env python

import subprocess
import argparse

DOCKER_CMD = 'docker run'
DOCKER_IMG = 'postgres:latest'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--mounts", nargs='+', type=str, default=None)
    parser.add_argument("--password", type=str, default='password')
    parser.add_argument("--user", type=str, default='admin')
    parser.add_argument("--db_name", type=str, default='time_manager')
    parser.add_argument("--port", type=int, default=5432)

    args = parser.parse_args()

    command = DOCKER_CMD

    if args.mounts:
        command = f'{command} {" ".join([f"-v {i}" for i in args.mounts])}'

    command = f'{command} -p {args.port}:5432 -e POSTGRES_PASSWORD={args.password} -e POSTGRES_USER={args.user} -e POSTGRES_DB={args.db_name} {DOCKER_IMG}'

    with subprocess.Popen(command, stdin=None, stderr=None, shell=True, universal_newlines=False) as p:
        p.communicate()
