function add_tests_bug(test_class, test_name, id)
{
      var s = document.getElementById("class_name");
      s.value = test_class;
      var x = document.getElementById("test_name");
      x.value = test_name;

      $("#add_tests_bug_modal").data('id', id).modal('show');
      $("#tests_bug_alert_div").addClass('hidden');
}
