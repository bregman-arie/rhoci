<script>
$(document).ready(function() {

$("#jobs_table").DataTable({
    "ajax": "{{ uf }}",
        "columns": [
          {"data": "className"},
          {"data": "name",
           "defaultContent": "None"
          },
          {"data": "status",
           "defaultContent": "None"
          },
          {"data": "Jobs",
           "defaultContent": "None"
          },
          ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
        status = aData.status;
        {% include "tables/color_result.js" -%}
        columnDefs: [
            {
                targets:[0, 1],
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                      return $('<a>')
                        .attr('href', '/jobs/{{ job_name }}/{{ build_num }}/' + row['className'] + '.' + row['name'])
                       .text(data)
                       .wrap('<div></div>')
                       .parent()
                       .html();
                      }
                  else { return data; }
                }
            },
            {
                targets:[3],
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[0] != 0){
                       data = '<a href="/tests/class/' + row['className'] + '/name/' + row['name'] + '">' + 'Jobs' + '</a>';
                    }
                    return data;
                }
            },
        ],
  search: { "regex": true }, 
  deferRender: true,
});

});
</script>
