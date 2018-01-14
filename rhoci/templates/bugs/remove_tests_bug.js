function remove_tests_bug(bug_num, test_class, test_name)
{
      var s = document.getElementById("remove_tests_bug_num");
      s.value = bug_num;
      var x = document.getElementById("remove_bug_test_class");
      x.value = test_class;
      var y = document.getElementById("remove_bug_test_name");
      y.value = test_name;
      $('#remove_tests_bug_modal').data('id', bug_num).data('test_class', test_class).data('test_name', test_name).modal('show');
}
