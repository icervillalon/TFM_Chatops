pipeline {
	agent {
	    docker {
	        image 'java-jenkins-slave:latest'
	        args '-v /var/run/docker.sock:/var/run/docker.sock'
	    }
	}

	stages {
		stage ("test") {
			steps {
				sh "python /home/jenkins/scripts/test.py -e pre"
			}
		}
	}
}