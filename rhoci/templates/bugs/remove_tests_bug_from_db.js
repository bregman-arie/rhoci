function remove_tests_bug_from_db()
{
  var all = $('#tests_remove_all').prop('checked');
  var id = $('#remove_tests_bug_modal').data('id');
  var test_class = $('#remove_tests_bug_modal').data('test_class');
  var test_name = $('#remove_tests_bug_modal').data('test_name');

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'bug_num': id, 'test_name': test_name, 'test_class': test_class, 'remove_all': all},
    url: "{{ url_for('home.remove_tests_bug') }}",
  });


  $('[data-id='+id+']').parents('tr').remove();
  $("#remove_tests_bug_modal").modal('hide');
}
