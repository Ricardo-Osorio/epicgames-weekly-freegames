`Still in development`
# Automatically get the epicgames store weekly free games
I like free games but I don't like repeating the same process over and over again when it can be automated... And that's why I made this!

## What it is
This is a simple python3.7 script making use of [selenium webdriver](https://selenium.dev/) and [chrome driver](https://sites.google.com/a/chromium.org/chromedriver/) to run run chrome in headless mode, navigate to the epicgames store, login into your account and redeem all weekly free games available. All of this inside of a docker container.

## Getting started
Personally I avoid hosting such processes on my machine so I don't have to worry about having it turned ON during the times when it's supposed to run. So I opt for deploying it into AWS ECS and completely forget it exists... until I check my account on the website that is! ;)

Build the image from the Dockerfile:
```
docker build -t epicgames .
```
Run a docker container from the newly built image:
```
docker run -e EMAIL=<EMAIL> -e PASSWORD=<PASSWORD> epicgames
```
Replacing the environment variables `EMAIL` and `PASSWORD` for your epicgames store credentials.

## Optional configuration
You can also specify two extra environmente variables `TIMEOUT` and `LOGIN_TIMEOUT` if you have a slow internet connection speed and want to make sure it won't affect the result of the script.
Run a docker container with these:
```
docker run -e TIMEOUT=10 -e LOGIN_TIMEOUT=15 -e EMAIL=<EMAIL> -e PASSWORD=<PASSWORD> epicgames
```
These environmente variables have a default value of `TIMEOUT = 5` and `LOGIN_TIMEOUT = 10`.
