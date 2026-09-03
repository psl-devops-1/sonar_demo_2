pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Persitent-python-PCCE/Isha-Harmalkar.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('p1_0') {
                    bat 'docker build -t midblue12/flask-lms:latest .'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-12',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                        echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin
                        if errorlevel 1 exit /b 1
                        
                        docker push midblue12/flask-lms:latest
                    '''
                }
            }
        }
    }
}