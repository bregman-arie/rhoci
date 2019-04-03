"fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    if ( aData.last_build.status == "FAILURE" )
    {
    $('td', nRow).css('background-color', '#f2dede' );
    }
    else if ( aData.last_build.status == "SUCCESS" )
    {
    $('td', nRow).css('background-color', '#dff0d8');
    }
    else if ( aData.last_build.status == "UNSTABLE" )
    {
    $('td', nRow).css('background-color', '#fcf8e3');
    }
},
