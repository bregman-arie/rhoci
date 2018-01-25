    $('#jobs_table').DataTable( {
      "ajax": "{{ url_for('jobs.get', result='FAILURE', dfg='DFG', release='RELEASE', failure_name='FL') }}".replace("FAILURE", result).replace("DFG", dfg_name).replace("RELEASE", release).replace("FL", failure_name),
      className: "text-center",
      "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
          if ( aData[1] == 'None' )
          {
          $('td', nRow).css('background-color', '#E8E8E8');
          }
          else if ( aData[1] == "SUCCESS" )
          {
          $('td', nRow).css('background-color', '#dff0d8');
          }
          else if ( aData[1] == "UNSTABLE" )
          {
          $('td', nRow).css('background-color', '#fcf8e3');
          }
          else
          {
          $('td', nRow).css('background-color', '#f2dede' );
          }
        },
        columnDefs: [
            {
                targets:0,
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                        data = '<a href="{{ agent.url }}/job/' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:1,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && (row[1] == 'UNSTABLE' || row[1] == 'SUCCESS')){
                        data = '<a href="{{ agent.url }}/job/' + row[0] + '/' + row[2] + '">' + data + '</a>';
                    }
                    else if (type === 'display' && row[1] == 'FAILURE') {
                    data = '<button type="button" onClick="analyze_failure(this, \'' + row[0] + '\', \'' + row[2] + '\')" class="btn btn-danger btn-lg">Failure - Tell me why!</button>'
                    }
                    else if (type === 'display' && row[1] != 'None' ){
                    data = '<button type="button" onClick="show_failure(\'' + row[0] + '\', \'' + row[2] + '\')" class="btn btn-danger btn-lg">FAILURE_NAME</button>'.replace("FAILURE_NAME", row[1])
                    }
                  return data;
                }
            },
            {
                targets:2,
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[2] != 0){
                        data = '<a href="{{ agent.url }}/job/' + row[0] + '/' + row[2] + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                targets:3,
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display' && row[2] != 0){
                    data = '<button type="button" onClick="show_tests(\'' + row[0] + '\', \'' + row[2] + '\')" class="btn btn-info btn-lg">Tests</button>'
                    }
                    return data;
                }
            },
            {
                targets:6,
                className: "text-center",
                render: function ( data, type, row, meta ) {
                    if(type === 'display'){
                    data = '<button type="button" id=\'' + row[0] +'\' onClick="add_bug(\'' + row[0] + '\', \'' + row[2] + '\', id)" class="btn btn-primary btn-lg" style="margin-right: 5px;">+</button>'
                      var arrayLength = row[6].length;
                      if(arrayLength > 0){
                        data = data + '<button id="button-'+ row[0] +'" type="button" onClick="show_bugs(\'' + row[0] + '\')" class="btn btn-danger btn-lg">Bugs</button>';
                      }
                    }
                    return data;
                }
            }
          ]
    } );
