app.controller('BugCtrl', function($scope) {

    $scope.choices = []
	
	$scope.addNewBug = function() {
			var newItemNo = $scope.choices.length+1;
			$scope.choices.push({'id':'choice'+newItemNo});
		  };
	  
  $scope.removeChoice = function(index) {   
      $scope.choices.splice(index, 1);
  };	  

});
