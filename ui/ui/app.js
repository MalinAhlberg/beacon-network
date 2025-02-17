'use strict';

// Declare app level module which depends on views, and components
angular.module('beaconApp', [
  'ngRoute',
  'beaconApp.view',
  'beaconApp.about',
  'beaconApp.newbeacon',
  'beaconApp.version'
]).
config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');

  $routeProvider.otherwise({redirectTo: '/view'});
}]);
