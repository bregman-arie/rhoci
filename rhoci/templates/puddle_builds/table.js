<script>
$(document).ready(function() {

$("#builds_table").DataTable({
    "ajax": "{{ uf }}",
        "columns": [
          {"data": "job_name",
           "defaultContent": ""
          },
          {"data": "status",
           "defaultContent": "None"
          },
          {"data": "number",
           "defaultContent": "None"
          },
          {"data": "timestamp",
           "defaultContent": "No Date"
          },
          ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
        status = aData.status;
        {% include "tables/color_result.js" -%}
        columnDefs: [
            {
                targets:0,
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                        data = '<a href="/jobs/' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[2],
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[3] != 0 ){
                          data = '<a href="/jobs/' + row['job_name'] + '/' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[1],
                render: function ( data, type, row, meta ) {
                  data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['number'] + '">' + data + '</a>';
                  return data;
                }
            },
            {
                targets:4,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[1] != 0 && (row['status'] == 'SUCCESS' || row['status'] == 'UNSTABLE')){
                    data = '<a href="/job/' + row['job_name'] + '/' + row['number'] + '/tests' + '">Tests</a>';
                    }
                    else {
                      data = 'No Tests';
                    }

                    return data;
                }
            },
            {
                targets:5,
                render: function ( data, type, row, meta ) {
          {% if current_user.is_anonymous %}
                    data = '<a href="' + "{{ jenkins_url }}" + '/job/' + '/consoleFull"><img src="{{ url_for('static', filename='images/terminal.png') }}">';
          {% else %}
                    data = '<a href="' + "{{ jenkins_url }}" + '/job/' + '/consoleFull"><img src="{{ url_for('static', filename='images/terminal.png') }}">   <a href="' + "{{ jenkins_url }}" + '/job/' + '/build"><img src="{{ url_for('static', filename='images/clock.png') }}">   <a href="' + "{{ jenkins_url }}" + '/job/' + '/configure"><img src="{{ url_for('static', filename='images/parameters.png') }}">  ';
          {% endif %}
                  return data;
                }
            },
        ],
  processing: true,
  search: { "regex": true }, 
  deferRender: true,
});

});
</script>
<!-- -->
