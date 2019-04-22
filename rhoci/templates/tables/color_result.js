    if ( status == "FAILURE" )
    {
    $('td', nRow).css('background-color', '#f2dede' );
    }
    else if ( status == "SUCCESS" )
    {
    $('td', nRow).css('background-color', '#dff0d8');
    }
    else if ( status == "UNSTABLE" )
    {
    $('td', nRow).css('background-color', '#fcf8e3');
    }
},
