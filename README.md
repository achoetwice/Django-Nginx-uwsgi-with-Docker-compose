## An example for Django+Nginx+uwsgi with Dcoker-compose
Here is the example of how to build a complete service with docker-compose. Docker-compose.yml and app.dockerfile should be helpful as a reference.\
But notice that, this project won't be working or doing anything functional, since there are environment variables not been provided by me, that's intentional.\
Make a project easy to deploy with docker, while it's hard to steal credential data use envfiles, that the idea.\
Also I've used Celery with RabbitMQ in docker compose to set schedule works.

## Credential file list
 - .env file for docker-compose variable(like nginx port)
 - Create a payment.env file to set env variables(like keys and iv for decrypt data)
 - mysite.sock in app to make Nginx and uwsgi communicate.
