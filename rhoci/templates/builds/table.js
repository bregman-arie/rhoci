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
                        data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['number'] + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[1],
                render: function ( data, type, row, meta ) {
                  console.log(row);
                  data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['number'] + '">' + data + '</a>';
                  return data;
                }
            },
            {
                targets:4,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[1] != 0 && (row['status'] == 'SUCCESS' || row['status'] == 'UNSTABLE')){
                    data = '<a href="' + "{{ jenkins_url }}" + '/job/' + row['job_name'] + '/' + row['number'] + '/testReport' + '">Tests</a>';
                    }
                    else {
                      data = 'No Tests';
                    }

                    return data;
                }
            },
        ],
  processing: true,
  search: { "regex": true }, 
});

});
</script>
<!-- -->
