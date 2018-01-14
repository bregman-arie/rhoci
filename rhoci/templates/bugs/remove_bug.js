function remove_bug(bug_num, job)
{
      var s = document.getElementById("remove_bug_num");
      s.value = bug_num;
      var x = document.getElementById("remove_bug_job");
      x.value = job;
      $('#remove_bug_modal').data('id', bug_num).data('job', job).modal('show');
}
