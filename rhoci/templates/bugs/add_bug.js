function add_bug(job, build, id)
{
      var s = document.getElementById("job_name");
      s.value = id;
      $("#add_bug_modal").modal();
      $("#bug_alert_div").addClass('hidden');
}
