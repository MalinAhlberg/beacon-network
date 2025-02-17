'use strict';

angular.module('beaconApp.newbeacon', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/newbeacon', {
    templateUrl: 'newbeacon/newbeacon.html',
    controller: 'NewBeaconCtrl'
  });
}])

.controller('NewBeaconCtrl', ['$scope', '$http', function($scope, $http) {

  $scope.beaconURL = '';
  $scope.beaconInfo = {};
  $scope.addNewBeaconMessage = '';
  $scope.apiKey = '';
  var registryURL = '';

  // Read registry URL from config file
  $http.get('newbeacon/config.json').success(function (data){
    registryURL = data.registryUrl;
  });

  $scope.fetchBeaconInfo = function() {
    if ($scope.beaconURL) {
      $scope.addNewBeaconMessage = '';
      $http({
        method: 'GET',
        url: $scope.beaconURL
      }).then(function successCallback(response) {
          $scope.beaconInfo = response.data;
          // Check if beacon info has Beacon Network items
          // If not, aka "Standalone Beacon", give default values
          if (!$scope.beaconInfo.hasOwnProperty('serviceType')) {
            $scope.beaconInfo.serviceType = 'GA4GHBeacon';
          }
          if (!$scope.beaconInfo.hasOwnProperty('serviceUrl')) {
            $scope.beaconInfo.serviceUrl = $scope.beaconURL;
          }
          if (!$scope.beaconInfo.hasOwnProperty('open')) {
            $scope.beaconInfo.open = true;
          }
          // document.getElementById("fetchedInfo").style.display = "block";
        }, function errorCallback(response) {
          // console.log(response);
      });
    }
  }

  $scope.isEmpty = function(obj) {
      for(var key in obj) {
          if(obj.hasOwnProperty(key))
              return false;
      }
      return true;
  }

  $scope.addNewBeacon = function() {
    var data = $scope.beaconInfo;
    var serviceUrl = $scope.beaconURL;
  
    if (!$scope.isEmpty(data)) {
      // console.log('have data');
      // construct proper payload form for POST /services
      var payload = {
        id: data.id,
        name: data.name,
        serviceType: data.serviceType,
        serviceUrl: data.serviceUrl,
        open: data.open,
        apiVersion: data.apiVersion,
        organization: {
          id: data.organization.id,
          name: data.organization.name,
          description: data.organization.description,
          address: data.organization.address,
          welcomeUrl: data.organization.welcomeUrl,
          contactUrl: data.organization.contactUrl,
          logoUrl: data.organization.logoUrl,
          info: {} // disabled till overhaul
        },
        description: data.description,
        version: data.version,
        welcomeUrl: data.welcomeUrl,
        alternativeUrl: data.alternativeUrl
      }
      // Register Beacon
      $http({
        method: 'POST',
        url: registryURL,
        data: payload,
        headers: {'Content-Type': 'application/json', 'Post-Api-Key': $scope.apiKey}
      }).then(function successCallback(response) {
          $scope.addNewBeaconMessage = `${response.data.message} : ${response.data.beaconServiceKey}`;
          // document.getElementById("fetchedInfo").style.display = "block";
        }, function errorCallback(response) {
          $scope.addNewBeaconMessage = response.data;
      });
    } else {
      // console.log('dont have data');
      $scope.addNewBeaconMessage = 'Provide info endpoint and pull data first.';
    }
  }


}]);
