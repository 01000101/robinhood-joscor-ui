var APP = angular.module('app', [
  'ngStorage', 'chart.js', 'ui.bootstrap'
]);

var API_ENDPOINT = 'http://localhost:5000';

// Main application
APP.controller('MainCtrl', [
  '$scope', '$localStorage', '$http',
  function MainCtrl($scope, $localStorage, $http) {
    $scope.progress = { val: 0, max: 0 };
    $scope.init = false;
    $scope.form_rh_token = '';
    $scope.user = null;
    $scope.orderby = 'total_cost';
    $scope.orderdir = true;
    $scope.positions = [];
    $scope.labels = [];
    $scope.data = [];
    $scope.error_msg = null;

    $scope.get_total_values = function() {
      var total = 0;
      for( var i = 0; i < $scope.positions.length; i++ )
        total += $scope.positions[i].quote.last_trade_price * $scope.positions[i].quantity;
      return total;
    };

    $scope.get_total_costs = function() {
      var total = 0;
      for( var i = 0; i < $scope.positions.length; i++ )
        total += $scope.positions[i].total_cost;
      return total;
    };

    $scope.get_total_percentages = function() {
      var total = 0;
      var ptotal = $scope.get_total_values();
      for( var i = 0; i < $scope.positions.length; i++ )
        total += ($scope.positions[i].quote.total_value / ptotal) * 100;
      return total;
    };

    function get_user_info(token, cb) {
      $http({
        method: 'GET',
        url: API_ENDPOINT + '/user',
        headers: {'RH-AUTH-TOKEN': token}
      }).then(function success(res) {
        //console.debug('Authenticated', res.data);
        cb(res.data.results);
      }, function error(res) {
        console.error('Failed authentication', res);
        $scope.error_msg = 'Authentication failed. Please check your ' +
                           'credentials and try again.';
        cb(null);
      });
    }

    function get_user_positions(token, cb) {
      if( !$scope.user || !token ) return;
      $http({
        method: 'GET',
        url: API_ENDPOINT + '/positions?hasquantity=1',
        headers: {'RH-AUTH-TOKEN': token}
      }).then(function success(res) {
        //console.debug('Response', res.data);
        cb(res.data.results);
      }, function error(res) {
        console.error('Error', res);
        $scope.error_msg = res.data.error || 'Unkonwn error getting positions';
      });
    }

    function get_instrument(token, id, cb) {
      if( !$scope.user || !token || !id ) return;
      $http({
        method: 'GET',
        url: API_ENDPOINT + '/instruments/' + id,
        headers: {'RH-AUTH-TOKEN': token}
      }).then(function success(res) {
        //console.debug('Response', res.data);
        cb(res.data.results);
      }, function error(res) {
        console.error('Error', res);
        $scope.error_msg = res.data.error || 'Unkonwn error getting instruments';
      });
    }

    function get_fundamental(token, symbol, cb) {
      if( !$scope.user || !token || !symbol ) return;
      $http({
        method: 'GET',
        url: API_ENDPOINT + '/fundamentals/' + symbol,
        headers: {'RH-AUTH-TOKEN': token}
      }).then(function success(res) {
        //console.debug('Response', res.data);
        cb(res.data.results);
      }, function error(res) {
        console.error('Error', res);
        $scope.error_msg = res.data.error || 'Unkonwn error getting fundamentals';
      });
    }

    function get_quote(token, symbol, cb) {
      if( !$scope.user || !token || !symbol ) return;
      $http({
        method: 'GET',
        url: API_ENDPOINT + '/quotes/' + symbol,
        headers: {'RH-AUTH-TOKEN': token}
      }).then(function success(res) {
        //console.debug('Response', res.data);
        cb(res.data.results);
      }, function error(res) {
        console.error('Error', res);
        $scope.error_msg = res.data.error || 'Unkonwn error getting quotes';
      });
    }

    function init(token) {
      get_user_info(token, function(user) {
        $scope.init = true;
        $scope.user = user;
        if( !$scope.user ) return;
        $localStorage.rh_auth_token = token;
        get_user_positions(token, function(positions) {
          $scope.positions = positions;
          $scope.progress.max = positions.length;
          for( var i = 0; i < $scope.positions.length; i++ )
            (function(i) {
              get_instrument(token, $scope.positions[i].instrument, function(instrument) {
                $scope.positions[i].instrument = instrument;
                $scope.labels.push(instrument.symbol);
                $scope.data.push($scope.positions[i].total_cost);
                $scope.progress.val += 0.4;
                get_fundamental(token, instrument.symbol, function(fundamental) {
                  $scope.positions[i].fundamental = fundamental;
                  $scope.progress.val += 0.3;
                });
                get_quote(token, instrument.symbol, function(quote) {
                  $scope.positions[i].quote = quote;
                  $scope.positions[i].quote.total_value =
                    ($scope.positions[i].quote.last_trade_price *
                     $scope.positions[i].quantity);
                  $scope.progress.val += 0.3;
                });
              });
            })(i);
        });
      });
    }

    // Init with new username & password
    $scope.authenticate_legacy = function(username, password) {
      $scope.error_msg = null;
      $http({
        method: 'POST',
        url: API_ENDPOINT + '/authenticate',
        data: {
          'username': username,
          'password': password
        }
      }).then(function success(res) {
        console.debug('Response', res.data);
        init(res.data.results.token);
      }, function error(res) {
        console.error('Error', res);
        $scope.error_msg = res.data.error || 'Unknown error';
      });
    };

    // Init with new token
    $scope.authenticate = function(token) {
      $scope.error_msg = null;
      init(token);
    };

    // Logout
    $scope.logout = function() {
      delete $localStorage.rh_auth_token;
      $scope.progress = { val: 0, max: 0 };
      $scope.user = null;
      $scope.init = true;
      $scope.positions = [];
    };

    // Init (with existing token in storage)
    console.debug('$localStorage', $localStorage);
    if( 'rh_auth_token' in $localStorage )
      init( $localStorage.rh_auth_token );
    else $scope.init = true;
  }
]);
