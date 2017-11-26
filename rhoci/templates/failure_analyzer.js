  // Assign variables from forms
  var job = $('#job_input').val();
  var build = $('#build_input').val();
  $("#alert_div").addClass('hidden');
  $("#loading_div").removeClass('hidden');
  $("#logs_table tr").remove(); 
  $("#logs_div").addClass('hidden');
  $("#failure_div").addClass('hidden');
  $("#info_div").addClass('hidden');

  input_validation();



function input_validation() {
  
  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'job': job, 'build': build},
    url: "{{ url_for('builds.exists') }}",
    success: function(response){
      console.log("begin");
      if (response.exists) {
        if (response.known_failure) {
          
          $("#failure_div").removeClass('hidden');
          var div = document.getElementById('failure_info_div');
          div.innerHTML += "<div class='alert alert-danger'>Found the failure: " + response.failure_line + "</div>";
          div.innerHTML += "<br>";
          div.innerHTML += "<div class='alert alert-info'>Cause: " + response.cause + "</div>";
          div.innerHTML += "<br>";
          div.innerHTML += "<div class='alert alert-success'> Suggested action: " + response.action + "</div>";
          $("#loading_div").addClass('hidden');
        
        }
        else {
        console.log("obtain logs!");
        obtain_logs();
        }
      }
      else {
        $("#alert_div").removeClass('hidden');
        $("#alert_div").text(response.message);
        $("#loading_div").addClass('hidden');
      }
    }
  });
  
  }

function obtain_logs() {

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'job': job, 'build': build},
    url: "{{ url_for('builds.obtain_logs') }}",
    success: function(response){
      if (response.found) {
        console.log(response.message);
        $("#logs_div").removeClass('hidden');
        var table = document.getElementById("logs_table");
        for(var i =0; i<(response.logs).length; i++) {
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = response.logs[i];
        }
        
        find_error(response.logs);

      }
      else {
        $("#alert_div").removeClass('hidden');
        $("#alert_div").text(response.message);
        $("#loading_div").addClass('hidden');
      }
    }
  });

}


function find_error(logs) {

  var found = false;
  var failure_name = '';

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'job': job, 'build': build},
    url: "{{ url_for('builds.find_failure') }}",
    success: function(response){
      if (response.found) {
      found = true;
      failure_name = response.failure_name;
      $("#failure_div").removeClass('hidden');
      var div = document.getElementById('failure_info_div');
      div.innerHTML += "<div class='alert alert-danger'>Found the failure: " + response.failure_line + "</div>";
      div.innerHTML += "<br>";
      div.innerHTML += "<div class='alert alert-info'>Cause: " + response.cause + "</div>";
      div.innerHTML += "<br>";
      div.innerHTML += "<div class='alert alert-success'> Suggested action: " + response.action + "</div>";
      }
      else {
      $("#alert_div").removeClass('hidden');
      var div = document.getElementById('alert_div');
      div.innerHTML += "I have no idea what is the problem :(";
      div.innerHTML += "<br>";
      div.innerHTML += "My developer did a terrible job in developing me. Perhaps you can help? <a href=https://github.com/bregman-arie/rhoci/blob/master/rhoci/common/failures.py> Failures list</a>";
      }
      $("#loading_div").addClass('hidden');
    }
  });

}

