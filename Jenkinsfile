pipeline {
    agent {
        docker { image 'my-jenkins:with-python' }
    }
    environment {
        PATH = "${env.PATH}:/usr/local/bin"
        VENV_DIR = 'venv'
        FLASK_APP = 'app.py'
    }
    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        stage('Setup Python Environment') {
            steps {
                sh 'python3 --version'
                sh 'python3 -m venv ${VENV_DIR}'
                sh 'ls -la ${VENV_DIR}/bin/'  // Debug step
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                if [ -f requirements.txt ]; then
                    pip install -r requirements.txt
                fi
                '''
            }
        }
        stage('Run Application') {
            steps {
                sh '. ${VENV_DIR}/bin/activate && python ${FLASK_APP} &'
            }
        }
    }
    post {
        always {
            script {
                sh 'pkill -f ${FLASK_APP} || true'
                sh 'rm -rf ${VENV_DIR} || true'
            }
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Debug information:'
        }
    }
}

