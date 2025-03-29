pipeline {
    agent any
    stages {
        stage('Build') {
            when {
                changeset "./kriging_app/realtime_krig/config.json"
            }
            steps {
                echo 'Building...'
                echo 'Preparing data extraction grid...'
                sh '''
                    cd ./kriging_app/realtime_krig
                    python prepare_grid.py
                    cd ../..
                    '''
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
