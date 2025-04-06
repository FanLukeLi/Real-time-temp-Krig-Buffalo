pipeline {
    agent { 
        node {
            label 'docker-agent-alpine'
            }
    }
    stages {
        stage('Build') {
            when {
                changeset "kriging_app/**"
            }
            steps {
                echo 'Building...'
                echo 'Building docker image'
                sh '''
                    cd kriging_app
                    {docker pull continuumio/miniconda3:latest} || {}
                    {docker rmi basic-krig-app:latest} || {}
                    {docker build -t basic-krig-app:latest .}
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
