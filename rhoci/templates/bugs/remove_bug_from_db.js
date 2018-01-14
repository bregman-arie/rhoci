function remove_bug_from_db()
{
  var all = $('#remove_all').prop('checked');
  var id = $('#remove_bug_modal').data('id');
  var job = $('#remove_bug_modal').data('job');

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'bug_num': id, 'job': job, 'test': 'y', 'remove_all': all},
    url: "{{ url_for('home.remove_bug') }}",
  });


  $('[data-id='+id+']').parents('tr').remove();
  $("#remove_bug_modal").modal('hide');
}
