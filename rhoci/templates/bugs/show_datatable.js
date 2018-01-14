function show_bugs(job, test_class, test_name)
{
      $('#bugs_table').DataTable( {
        "ajax": {
          "data": {'job': job, 'test_class': test_class, 'test_name': test_name},
          "url": "{{ url_for('home.get_bugs_datatable') }}",
        },
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if ( aData[2] == "CLOSED" )
            {
            $('td', nRow).css('background-color', '#dff0d8');
            }
            if ( aData[2] == "NEW" )
            {
            $('td', nRow).css('background-color', '#f2dede' );
            }
            if ( aData[2] == "ASSIGNED" )
            {
            $('td', nRow).css('background-color', '#fcf8e3');
            }
        },
        columnDefs: [
            {
                targets:[4],
                className: "text-center",
                render: function ( data, type, row, meta ) {
                        if (job === undefined || job === null || job === '') {
                        data = '<button type="button" onClick="remove_tests_bug(\'' + row[1] + '\', \'' + test_class + '\', \'' + test_name + '\')" data-id=\'' + row[1] +'\' data-test=\'' + test_name + '\' class="btn btn-info btn-lg">remove</button>'
                        }
                        else {
                        data = '<button type="button" onClick="remove_bug(\'' + row[1] + '\', \'' + job + '\')" data-id=\'' + row[1] +'\' class="btn btn-info btn-lg">remove</button>'
                        }
                        return data;
                }
            },
            {
                targets:[0, 1],
                className: "text-center",
                render: function ( data, type, row, meta ) {
                        data = '<a href="http://bugzilla.redhat.com/' + row[1] + '">' + data + '</a>';
                        return data;
                }
            },
          ],
      });

      document.getElementById("modal-title-bugs").innerHTML = job + "  bugs";
      $("#bugs_modal").modal({show:true, backdrop: false});
}
