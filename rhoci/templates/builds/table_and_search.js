<script>

{% include "builds/filter_widget.js" -%}

$('#menu li:nth-child(1) a').addClass('active');
$("#execute_button").css('display', 'inline');
$("#graph_button").css('display', 'inline');

var filters_array = [];
{% for filter in filters %}
    var filter_tuple = ["{{ filter[0]|safe }}", String("{{ filter[1]|safe }}"), {{ filter[2]|safe }}];
    filters_array.push(filter_tuple);
{% endfor %}
init_filter_widget(filters_array, function() {get_results(filters_array)});

$("#builds_table").DataTable({
    "ajax": "{{ uf }}",
        "columns": [
          {"data": "job_name",
           "defaultContent": ""
          },
          {"data": "status",
           "defaultContent": "None"
          },
          {"data": "build_number",
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
                  data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['build_number'] + '">' + data + '</a>';
                  return data;
                }
            },
            {
                targets:4,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[1] != 0 && (row['status'] == 'SUCCESS' || row['status'] == 'UNSTABLE')){
                    data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['build_number'] + '/testReport' + '">Tests</a>';
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
  select: true,
  search: { "regex": true }, 
  deferRender: true,
});
</script>
