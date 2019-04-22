render: function ( data, type, row, meta ) {
  data = '<a href="' + "{{ jenkins_url }}" + '/job/' + job_name + '/' + build_num + '">' + build_status + '</a>';
  return data;
}
