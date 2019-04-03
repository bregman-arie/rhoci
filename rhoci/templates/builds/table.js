<script>
$(document).ready(function() {

$("#builds_table").DataTable({
    "ajax": "{{ uf }}",
        "columns": [
          {"data": "name",
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
            console.log(aData)
            if ( aData.status == "FAILURE" )
            {
            $('td', nRow).css('background-color', '#f2dede' );
            }
            else if ( aData.status == "SUCCESS" )
            {
            $('td', nRow).css('background-color', '#dff0d8');
            }
            else if ( aData.status == "UNSTABLE" )
            {
            $('td', nRow).css('background-color', '#fcf8e3');
            }
        },
        columnDefs: [
            {
                targets:0,
                "visible": false,
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                        data = '<a href="/job/' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[2],
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[3] != 0 ){
                        data = '<a href="/job/' + row['job_name'] + '/' + row['last_build_number'] + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[1],
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && (row[1] == 'UNSTABLE' || row[1] == 'SUCCESS' || row[1] == 'ABORTED' || row[1] == null)){
                        data = '<a href="/job/' + row[1] + '/' + row[2] + '">' + data + '</a>';
                    }
                    else if (type === 'display' && row[1] == 'FAILURE') {
                    data = '<button type="button" onClick="analyze_failure(this, \'' + row[1] + '\', \'' + row[3] + '\')" class="btn btn-danger btn-lg">Failure</button>'
                    }
                    else if (type === 'display' && row[1] != 'None' ){
                    data = '<button type="button" onClick="show_failure(\'' + row[1] + '\', \'' + row[3] + '\')" class="btn btn-danger btn-lg">FAILURE_NAME</button>'.replace("FAILURE_NAME", row[1])
                    }
                    return data;
                }
            },
            {
                targets:4,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[1] != 0 && (row[1] == 'SUCCESS' || row[1] == 'UNSTABLE')){
                    data = '<button type="button" onClick="show_tests(\'' + row[1] + '\', \'' + row[3] + '\')" class="btn btn-info btn-lg">Tests</button>'
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
