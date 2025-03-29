pipeline {
    agent any
    stages {
        stage('Build') {
            when {
                changeset "kriging_app/**"
            }
            steps {
                echo 'Building...'
                echo 'Building docker image'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
