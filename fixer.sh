#!/bin/bash

if [ ! -d logs ]; then
	mkdir logs
fi
if [ ! -d data ]; then
	mkdir data
fi
if [ ! -f config/srv.conf ]; then
    cp config/srv.conf.bak config/srv.conf
fi
touch data/known_clients.conf
touch data/sessions.dat
touch data/known_topics.conf
touch data/retained_messages.dat
