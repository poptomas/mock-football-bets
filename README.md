# Mock Football Bets

## Table of contents
- [Brief description](#brief-description)
- [Motivation](#motivation)
- [Technology used](#technology-used)
- [Setup and launch](#setup-and-launch)

## Introduction
### Brief Description
Mock Football Bets is a web application which serves as an assistance for football bets. Within the application there is no real money involved, an user can make use of the virtual currency and place the bets as if they were real. Therefore it is primarily meant as a training platform. Furthermore, there are 3 modes where 2 of which utilize machine learning:
- Classic Mode - beforementioned mock bets
- Assist Mode - for the displayed bets, the application highlights the predicted result for a particular match
- Auto Mode - after specifying constraints on the machine in this mode (more in the section auto mode), the machine decides which matches should be chosen for a bet, how much money should be devoted to it and accomplishes bets itself.
Furthermore, an user can track his own bets history (including the bets accomplished by in the auto mode).

### Motivation
The main motivation for training platform creation was that it would enable even such users who are not in a situation to devote money aside for bets or have not reached appropriate age yet. Furthermore, let people get to know online betting using artificial intelligence. As a bonus, it may have been nice not to be the one to check the bets but let AI decide on its own.
Web applications which could serve the purpose as the author thought the project could look like could be [Oddin.gg](https://oddin.gg). Although Oddin offers AI-powered automated live odds, it is focused on esports, not classic sports and most importantly the services provided are not for free which is for the automated parts the largest issue.
From free services, there is [Kickoff](https://kickoff.ai/) which does not show exactly odds, nevertheless, it shows percentage of which result is found to be the most probable in a given match, therefore it may be well as a reference to "manual classic" bets for public.

## Technology used
- Python 3.9.7
- ReactJS 17.0.2
- XAMPP v3.3.0 - MySQL (port 3306), Apache (80/443)

## Setup and launch
- It is demanded to have at least [Python](https://www.python.org/downloads/release/python-397/) 3.8.5 and downloaded [node.js](https://nodejs.org/en/) 14+, [XAMPP](https://www.apachefriends.org/download.html) version 7.3.30+
- In the directory windows or linux up to your OS there is an install script (.bat for windows, .sh for linux)
- Database - localhost/phpmyadmin - create database "mfb" - import mfb.sql from root directory
- Make use of the run script in the windows or linux directory
- All should be up and running (it should launch automatically the website localhost:3000) - for a more detailed procedure, take a look at the user documentation

## Hardware requirements
- Minimal requirements are not set, in the documentation is the specification of the machine where the project was launched without any observable limitations which could be set as recommmendend hardware requirements