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
          {"data": "duration",
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
        ],
  processing: true,
  search: { "regex": true }, 
  deferRender: true,
});

});
</script>
