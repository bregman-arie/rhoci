function show_failure(job, build)
{
  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'job': job, 'build': build},
    url: "{{ url_for('builds.get_failure') }}",
    success: function(response){
      document.getElementById("failure-modal-title").innerHTML = job + "  Build#" + build ;
      var div = document.getElementById('failure_info_div');
      div.innerHTML = "";
      div.innerHTML += "<div class='alert alert-danger'>Found the failure: " + response.failure_text + "</div>";
      div.innerHTML += "<br>";
      div.innerHTML += "<div class='alert alert-info'>Cause: " + response.failure_cause + "</div>";
      div.innerHTML += "<br>";
      div.innerHTML += "<div class='alert alert-success'> Suggested action: " + response.failure_action + "</div>";
      document.getElementById("failure-modal-title").innerHTML = job + "  Build#" + build;
      $("#failure_modal").modal();
    }
  });

}
