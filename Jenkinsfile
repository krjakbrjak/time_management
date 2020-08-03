pipeline {
   agent {
     docker {
       image 'docker/compose:latest'
     }
   }
   stages {
     stage('Build') {
       steps {
        sh label: 'Building images', script: '''
            docker-compose up --build -d;
        '''
      }
    }

    stage('Unit Test') {
      steps {
          sh label: 'Running unit tests', returnStatus: true, script: '''
            docker-compose exec -T dev src/manage.py test src;
          '''
          // Copy output of tests from container to the host, so that it can be used by junit plugin
          sh label: 'Copying tests results from the container', returnStatus: true, script: '''
            docker-compose exec -T dev cat test-results.xml > test-results.xml;
          '''
          junit 'test-results.xml'
      }
    }
  }
    post {
      always {
        sh label: 'Stop running containers', returnStatus: true, script: '''docker-compose stop'''
      }
    }
}
