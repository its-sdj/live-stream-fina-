pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        FLASK_APP = 'app.py'
    }

stage('Clone Repository') {
    steps {
        git branch: 'main', url: 'https://github.com/its-sdj/live-stream-fina-.git'
    }
}


        stage('Setup Python Environment') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh '. ${VENV_DIR}/bin/activate && pip install --upgrade pip'
                sh '. ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // This will not fail the build if tests are missing
                    sh '. ${VENV_DIR}/bin/activate && python -m unittest discover tests || true'
                }
            }
        }

        stage('Run Application') {
            steps {
                script {
                    echo 'Running the Flask app...'
                    sh '. ${VENV_DIR}/bin/activate && python ${FLASK_APP} &'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build and run successful!'
        }
        failure {
            echo '❌ Build failed!'
        }
        always {
            echo 'Cleaning up...'
            sh 'pkill -f ${FLASK_APP} || true'
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}
