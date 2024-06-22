# Weird name?

Yeah I typo'd it on creating the project and couldn't be assed to fix it.

# Screenshots

**The Web Client**
![image](https://github.com/lili7h/remote_toys/assets/85176789/07d44556-2d2b-4322-b66b-5b74b48e9dac)


# Using
## Dev
`poetry run dev` will serve with the basic development Flask HTTP server 

## Prod
`poetry run prod` will serve using `Waitress`

## Deploying/Serving Externally
If you want to expose the local webserver externally, you can use Ngrok. Make sure you have your API key set.

Getting Ngrok: [medium.com guide](https://medium.com/automationmaster/how-to-use-ngrok-to-forward-my-local-port-to-public-5e9b148ff31c)

`ngrok http --domain=<your perma Ngrok domain>.ngrok-free.app 8080`

---

# Direct serving and deployment commands

## Serve
Can be invoked with a `poetry run prod`

`waitress-serve --listen *:8080 --call partner:myapp`


## Deploy

`ngrok http --domain=<your perma Ngrok domain>.ngrok-free.app 8080`
