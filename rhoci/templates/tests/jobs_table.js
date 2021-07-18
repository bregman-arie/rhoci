<script>
$(document).ready(function() {

$("#jobs_table").DataTable({
    "ajax": "{{ uf }}",
        "columns": [
          {"data": "job_name",
           "defaultContent": ""
          },
          {"data": "build_number",
           "defaultContent": "None"
          },
          {"data": "status",
           "defaultContent": "None"
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
            }
        ],
  dom: 'Plfrtip',
  select: true,
  search: { "regex": true }, 
  deferRender: true,
});

});
</script>
