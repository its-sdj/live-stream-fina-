pipeline {
    agent any

    environment {
        VENV_PATH = "venv"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git url: 'https://github.com/its-sdj/live-stream-fina-.git', branch: 'main'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    which python3 || echo "Python3 is not installed!"
                    python3 --version
                    python3 -m venv ${VENV_PATH}
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                '''
            }
        }

        stage('Run Application') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    python app.py &
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
                pkill -f app.py || true
                rm -rf ${VENV_PATH}
            '''
        }
    }
