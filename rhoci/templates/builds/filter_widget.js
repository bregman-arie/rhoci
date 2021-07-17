
function get_filter(filters, filter_name) {
    for (filter of filters) {
        // Convert from <class 'int'> to int
        if (filter[1].indexOf('<') > -1) {
            var start = filter[1].indexOf("\'") + 1;
            var end = filter[1].lastIndexOf("\'");
            filter[1] = filter[1].slice(start, end);
        };
        if (filter_name === filter[0]) {
            return filter;
        };
    };
};

function set_filter_value_hint(filters) {
    selection = $('#filter_key').val();
    filter = get_filter(filters, selection);
    if (filter[2] === null) {
        var input_type = filter[1];
        if (input_type == 'datetime.date') {
            input_type = 'yyyy-mm-dd';
        };
        var filter_value_tag = '<input type="text" name="filter_value" id="filter_value" style="width: 100%;" placeholder="' + input_type + '"">';
        $('#filter_value_container').html(filter_value_tag);
    }
    else {
        var filter_value_tag = '<select class="js-example-basic-single" id="filter_value" style="width: 100%;">'
        for (var option of filter[2]) {
            filter_value_tag += '<option value="' + option + '">' + option + '</option>';
        };
        '</select>';
        $('#filter_value_container').html(filter_value_tag);
        $('#filter_value').select2();
    };
}

function get_active_filter() {
    return $.url('?');
};

function get_filter_bubble(filter_name) {
    result = null;
    $('#selected_filters').children().each(function () {
        var key_value = $(this).children('.content').text().split('=');
        if (key_value[0] === filter_name) {
            result = $(this);
        };
    });
    return result;
};

function enable_filter_error(message) {
    $('#filter_error').text(message);
    $('#filter_error').show();
    $('#graph_button').prop('disabled', true);
};

function disable_filter_error() {
    $('#filter_error').text('');
    $('#filter_error').hide();
    $('#graph_button').prop('disabled', false);
};

function add_filter(filters) {
    add_filter_pill($("#filter_key").val(), $("#filter_value").val())
    update_url_parameters();
};

function add_filter_pill(k, v) {
    if (v.length == 0)
        return

    $('#selected_filters').append(
        "<li class='select2-selection__choice'><span class='select2-selection__choice__remove' role='presentation'>×</span><span class='content'>" + k + "=" + v + "</span></li>"
    );
};

function get_active_filter_from_ui() {
    var key_values = {}
    $('#selected_filters').children().each(function () {
        var key_value = $(this).children('.content').text().split('=');
        k = key_value[0];
        v = key_value[1];

        // Is the key being added again?
        if (k in key_values) {
            // Was the key already present more than once? If so, concat to the existing list
            if (key_values[k][0] == '[') {
                key_values[k] = key_values[k].slice(0, -1) + ',' + v + ']';
            } else { // This is only the second time the key is added, create the list
                key_values[k] = '[' + key_values[k] + ',' + v + ']';
            }
        } else {
            key_values[k] = v;
        };
    });
    return key_values
};

function update_url_parameters(report='') {
    var active_filters = get_active_filter_from_ui();
    parameters = '?';
    for (var key in active_filters) {
        var value = active_filters[key];
        parameters += key + '=' + value + '&';
    };
    if (parameters != '?') {
        parameters = parameters.slice(0, -1); // Remove last '&' char
    };
    if (report != '') {
        parameters = "/report/" + report + parameters;
    }
    window.history.pushState('', '', parameters);
};

function sort_selection(element_id) {
    var filter_options = $("#" + element_id + " option");
    filter_options.sort(function(a,b) {
        if (a.text > b.text) return 1;
        else if (a.text < b.text) return -1;
        else return 0
    })
    $("#" + element_id).empty().append(filter_options);
};

function update_ui_from_url() {
    active_filters = get_active_filter();
    for (var k in active_filters) {
        var v = active_filters[k];

        if (v[0] == '[') {
            // v is a list, remove [ and ] chars, iterate through elements
            for (list_element of v.substring(1, v.length - 1).split(',')) {
                add_filter_pill(k, list_element);
            };
        } else {
            add_filter_pill(k, v);
        };
    };
};

function init_filter_widget(filters, execute_query, report=false) {
    $('#filter_key').change(function() {
        set_filter_value_hint(filters);
    });

    $("#execute_button").click(execute_query);
    $("#add_filter").click(function() {add_filter(filters)});
    $("#run_recipe_button").click(function() {run_recipe(document.getElementById('recipe_key').value)});
    $(document).on("keypress", "#filter_value", function(event) {
        if (event.keyCode == 13) {
            add_filter(filters);
        };
    });

    $(document).on("click", ".select2-selection__choice__remove", function(){
        $(this).parent().remove();
        update_url_parameters();
    });

    spinner = null;
$(document).ready(function() {
        var opts = {
            lines: 13, // The number of lines to draw
            length: 20, // The length of each line
            width: 10, // The line thickness
            radius: 30, // The radius of the inner circle
            corners: 1, // Corner roundness (0..1)
            rotate: 0, // The rotation offset
            direction: 1, // 1: clockwise, -1: counterclockwise
            color: '#000', // #rgb or #rrggbb or array of colors
            speed: 1, // Rounds per second
            trail: 60, // Afterglow percentage
            shadow: false, // Whether to render a shadow
            hwaccel: false, // Whether to use hardware acceleration
            className: 'spinner', // The CSS class to assign to the spinner
            zIndex: 2e9, // The z-index (defaults to 2000000000)
            top: '50%', // Top position relative to parent
            left: '50%' // Left position relative to parent
        };
        spinner = new Spinner(opts);
    
        sort_selection('filter_key');
        set_filter_value_hint(filters);
        $('.js-example-basic-single').select2();
        if (! report) {
          update_ui_from_url();
        }
        execute_query();
    });
}; 
