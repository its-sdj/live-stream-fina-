pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        FLASK_APP = 'app.py'
    }

    stages {
        // Stage to clone the repository
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/its-sdj/live-stream-fina-.git'
            }
        }

        // Stage to set up Python environment
        stage('Setup Python Environment') {
            steps {
                // Set up Python virtual environment
                sh 'python3 -m venv ${VENV_DIR}'
                
                // Upgrade pip
                sh '. ${VENV_DIR}/bin/activate && pip install --upgrade pip'
                
                // Install the dependencies from requirements.txt
                sh '. ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
            }
        }

        // Stage to run the Flask application
        stage('Run Application') {
            steps {
                script {
                    echo 'Running the Flask app...'
                    sh '''
                    if [ -f ${VENV_DIR}/bin/activate ]; then
                        . ${VENV_DIR}/bin/activate
                    else
                        . ${VENV_DIR}/Scripts/activate
                    fi
                    python ${FLASK_APP} &
                    '''
                }
            }
        }

        // Additional stages like testing, setup, etc. can go here
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
            pkill -f ${FLASK_APP} || true
            rm -rf ${VENV_DIR}
            '''
        }
    }
}
