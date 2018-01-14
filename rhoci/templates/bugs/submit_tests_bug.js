function submit_tests_bug()
{
  var tests_bug_num = document.getElementById("tests_bug_num").value;
  var test_class = document.getElementById("class_name").value;
  var test_name = document.getElementById("test_name").value;
  var id = $('#add_tests_bug_modal').data('id');
  var apply_on_class = $('#apply_on_class').prop('checked');

  $("#tests_bug_alert_div").addClass('hidden');
  $("#add_tests_bug_spinner").removeClass('hidden');

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'bug_num': tests_bug_num, 'test_class': test_class, 'test_name': test_name, 'apply_on_class': apply_on_class},
    url: "{{ url_for('home.bug_exists') }}",
    success: function(response){
      $("#add_tests_bug_spinner").addClass('hidden');
      if (response.exists) {
        if ($('#button-' + test_class).length == 0) {
      $( '<button id="button-'+ id +'" type="button" style="margin-right: 5px;" onClick="show_bugs(\'\', \'' + test_class + '\', \'' + test_name + '\')" class="btn btn-danger btn-lg">Bugs</button>' ).insertAfter( "#" + id );
        }
      $("#add_tests_bug_modal").modal('hide');
      }
  else {
        $("#add_tests_bug_spinner").addClass('hidden');
        $("#tests_bug_alert_div").removeClass('hidden');
        $("#tests_bug_alert_div").text(response.err_msg);
  }
    }
  });
}
