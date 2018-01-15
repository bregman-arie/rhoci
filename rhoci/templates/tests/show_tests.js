function show_tests(job, build)
{
      $('#tests_table').DataTable( {
        "ajax": {
          "data": {'job': job, 'build': build},
          "url": "{{ url_for('tests.get_tests_datatable') }}",
        },
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if ( aData[2] == "PASSED" )
            {
            $('td', nRow).css('background-color', '#dff0d8');
            }
            else if ( aData[2] == "FAILED" || aData[2] == "REGRESSION" )
            {
            $('td', nRow).css('background-color', '#f2dede' );
            }
            else
            {
            $('td', nRow).css('background-color', '#d9edf7');
            }
          },
        columnDefs: [
            {
                targets:[0, 1],
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && data != 'No tests'){
                        replacement = '/';
                        old_class_name = row[0];
                        old_test_name = row[1];
                        class_name = old_class_name.replace(/\.([^\.]*)$/,replacement+'$1');
                        var test_name = old_test_name.replace(/-/g, "_").replace('[', '_').replace(']', '_').replace(/,/g, "_").replace(/ /g,"_").replace(/\(/g, "_").replace(/\)/g, "_");
                        data = '<a href="{{ agent.url }}/job/' + job + '/' + build + '/testReport/' + class_name + '/' + test_name + '">' + data + '</a>';
                    }
                    return data;
                }
            },
          {
                targets:5,
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                    data = '<button type="button" id=\'' + meta.row + meta.col + '\' onClick="add_tests_bug(\'' + row[0] + '\', \'' + row[1] + '\', id)" class="btn btn-primary btn-lg" style="margin-right: 5px;">+</button>'
                      var arrayLength = row[5].length;
                      if(arrayLength > 0){
                        data = data + '<button id="button-'+ row[0] +'" type="button" onClick="show_bugs(\'\', \'' + row[0] + '\', \'' + row[1] + '\')" class="btn btn-danger btn-lg">Bugs</button>';
                      }
                    }
                  return data;
                }
          },
          ],
      });
      document.getElementById("modal-title-tests").innerHTML = job + "  Build#" + build;
      $("#tests_modal").modal();

}

    $('#failed_tests_table').DataTable( {
        "ajax": "{{ url_for('tests.failing_tests_dfg', dfg=dfg) }}",
    "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
        $('td', nRow).css('background-color', '#f2dede' );
    },
    columnDefs: [
            {
                targets:[0, 1],
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && data != 'No tests'){
                        replacement = '/';
                        old_class_name = row[0];
                        old_test_name = row[1];
                        class_name = old_class_name.replace(/\.([^\.]*)$/,replacement+'$1');
                        var test_name = old_test_name.replace(/-/g, "_").replace('[', '_').replace(']', '_').replace(/,/g, "_").replace(/ /g,"_").replace(/\(/g, "_").replace(/\)/g, "_");
                        data = '<a href="{{ agent.url }}/job/' + row[2] + '/' + row[3] + '/testReport/' + class_name + '/' + test_name + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:[5, 6],
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && data != 'No bugs'){
                        data = '<a href="http://bugzilla.redhat.com/' + row[8] + '">' + data + '</a>';
                    }
                    return data;
                }
            },
          {
                targets:7,
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                    data = '<button type="button" id=\'' + meta.row + '\' onClick="add_tests_bug(\'' + row[0] + '\', \'' + row[1] + '\', id)" class="btn btn-primary btn-lg" style="margin-right: 5px;">+</button>'
                      var arrayLength = row[7].length;
                      if(arrayLength > 0){
                        data = data + '<button id="button-'+ row[0] +'" type="button" onClick="show_bugs(\'\', \'' + row[0] + '\', \'' + row[1] + '\')" class="btn btn-danger btn-lg">Bugs</button>';
                      }
                    }
                  return data;
                }
          }
          ],
    });
