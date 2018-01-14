function submit_bug()
{
  var bug_num = document.getElementById("bug_num").value;
  var bug_cell_id = document.getElementById("job_name").value;
  $("#bug_alert_div").addClass('hidden');
  $("#add_bug_spinner").removeClass('hidden');

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'bug_num': bug_num, 'job_name': bug_cell_id},
    url: "{{ url_for('home.bug_exists') }}",
    success: function(response){
      $("#add_bug_spinner").addClass('hidden');
      if (response.exists) {
        if ($('#button-' + bug_cell_id).length == 0) {
      $( '<button id="button-'+ bug_cell_id +'" type="button" style="margin-right: 5px;" onClick="show_bugs(\'' + bug_cell_id + '\')" class="btn btn-danger btn-lg">Bugs</button>' ).insertAfter( "#" + bug_cell_id );
        }
      $("#add_bug_modal").modal('hide');
      }
  else {
        $("#add_bug_spinner").addClass('hidden');
        $("#bug_alert_div").removeClass('hidden');
        $("#bug_alert_div").text(response.err_msg);
  }
    }
  });
}
