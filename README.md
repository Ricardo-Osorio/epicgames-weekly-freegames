# Automatically get the epicgames store weekly free games
I like free games but I don't like repeating the same process over and over again when it can be automated... And that's why I made this!

## What it is
This is a simple python3.7 script making use of [selenium webdriver](https://selenium.dev/) and [chrome driver](https://sites.google.com/a/chromium.org/chromedriver/) to run run chrome in headless mode, navigate to the epicgames store, login into your account and redeem all weekly free games available. All of this inside of a docker container.

## Getting started
Personally I avoid hosting such processes on my machine so I don't have to worry about having it turned ON during the times when it's supposed to run. So I opt for deploying it to AWS FARGATE and completely forget it exists... until I check my account on the website that is! ;)

#### Locally (Docker)
To run it locally, pull the image from docker-hub:
```
docker pull ricosorio/epicgames-weekly-freegames:latest
```
And run a docker container from the newly downloaded image:
```
docker run -e EMAIL=<EMAIL> -e PASSWORD=<PASSWORD> ricosorio/epicgames-weekly-freegames
```
Replacing the environment variables `EMAIL` and `PASSWORD` for your epicgames store credentials.

#### AWS Cloud (Fargate)
To run the image AWS Fargate (ECS) start by creating a task definition that that pulls the image from `ricosorio/epicgames-weekly-freegames:latest`. Note that you don't need to specify the host (by default it pulls from docker-hub).

When it comes to how much resources the container needs, I find it enough to have 0.5GB and lowest version of CPU - 0.25.

## Optional configuration
Different options can be provided to alter the output or execution of the program. All available options are:

- `TIMEOUT` and `LOGIN_TIMEOUT` if you have a slow internet connection speed and want to make sure it won't affect the result of the script. Defaults to `TIMEOUT = 5` and `LOGIN_TIMEOUT = 10`.

- `LOGLEVEL` can be used to specify the [log level](https://docs.python.org/3.7/library/logging.html#logging-levels) to log. Defaults to `INFO`

- `SLEEPTIME` can be used to set the number of seconds to wait between looping through the procedure again. Defaults to `-1`, which will stop execution after a single iteration.

- `TOTP` is used to log in to an account protected with 2FA. If you have 2FA enabled already, you may have to redo it in order for to obtain your TOTP token. Go [here](https://www.epicgames.com/account/password) to enable 2FA. Click "enable authenticator app." In the section labeled "manual entry key," copy the key. Then use your authenticator app to add scan the QR code. Activate 2FA by completing the form and clicking activate. Once 2FA is enabled, use the key you copied as the value for the `TOTP` parameter.

- `DEBUG` allows the script to be run locally without having to manually edit the chromedriver path (instead will searches in the current dir) and will ignore the headless flag when starting up chrome. Only checks for the presence of this environment variable, its value is not interpreted.

Running a docker container with these:
```
docker run -e TIMEOUT=15 -e LOGIN_TIMEOUT=20 -e LOGLEVEL=DEBUG -e SLEEPTIME=43200 -e EMAIL=<EMAIL> -e PASSWORD=<PASSWORD> ricosorio/epicgames-weekly-freegames
```

## Docker Compose
```
version: '2'

services:

    egs-freegame:
        build:
            context: ./epicgames-weekly-freegames/
            dockerfile: Dockerfile
        restart: always
        environment:
            - TIMEOUT=10
            - LOGIN_TIMEOUT=15
            - SLEEPTIME=43200
            - LOGLEVEL=DEBUG
            - EMAIL=example@example.com
            - PASSWORD=password123
```
