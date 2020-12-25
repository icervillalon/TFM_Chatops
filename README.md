## TFM Ignacio Cervantes

TFM based on a ChatOps integration with RASA chatbot, Jenkins and Docker.

## Jenkins docker installation
1. Open up a command prompt window and similar to the macOS and Linux instructions above do the following:

2. Create a bridge network in Docker

	docker network create jenkins

3. Run a docker:dind Docker image

	docker run --name jenkins-docker --rm --detach ^
	  --privileged --network jenkins --network-alias docker ^
	  --env DOCKER_TLS_CERTDIR=/certs ^
	  --volume jenkins-docker-certs:/certs/client ^
	  --volume jenkins-data:/var/jenkins_home ^
	  docker:dind

4. Build a customised official Jenkins Docker image using above Dockerfile and docker build command.

5. Run your own myjenkins-blueocean:1.1 image as a container in Docker using the following docker run command:

	docker run --name jenkins-blueocean --rm --detach ^
	  --network jenkins --env DOCKER_HOST=tcp://docker:2376 ^
	  --env DOCKER_CERT_PATH=/certs/client --env DOCKER_TLS_VERIFY=1 ^
	  --volume jenkins-data:/var/jenkins_home ^
	  --volume jenkins-docker-certs:/certs/client:ro ^
	  --publish 8080:8080 --publish 50000:50000 myjenkins-blueocean:1.1

6. Proceed to the Setup wizard.

### Rasa deployment
* To train the model -> rasa train
* To launch the chatbot with the stored model -> rasa run (or rasa shell for testing purposes)

It is mandatory to run an action server to perform custom actions logic. To do so, run "rasa run actions".

To connect with Telegram, ngrok is used to proxy the petitions to the localhost. To launch ngrok, execute "path_to_ngrok http 5005". The given URL must be placed in "credentials.yml" file to be accesible from Telegram.

## Jenkins plugins needed:
* Gitlab (used to integrate change detections in gsi Gitlab)
