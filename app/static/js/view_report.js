$(document).ready(function() {

    //select_report onChange event
    $('#select_report').on('change', function () {

        // exit function if the first default option is selected in the "select_report" dropdown
        if ($('#select_report :selected').prop("hidden") == true){
            return;
        }

        //assign current report title to the header
        $('#report_title').text($('#select_report :selected').text())

        //assign current value to the tool tip
        assign_selected_option_to_tooltip ($('#select_report'), $('#select_report :selected'));

        //console.log($('#select_report :selected').attr('helptip'));
        enable_popover(
            $('#select_report :selected').attr('helptip').split("|")[0],
            $('#select_report :selected').attr('helptip').split("|")[1]
        );

        //hide currently shown report
        $('#div_report').hide();

        $.post("/get_report_filters",
        {
            report_id: this.value,
            cur_program_id: $('#program_id').val() ? $('#program_id').val() : ""
        },
        function(data,status){
          if (status == 'success'){
            //TODO: check if this is needed
            //save study_id and associated program id for the currently selected in the study id select control
            if ($('#study_id').length > 0) {
                current_study_id = $('#study_id option:selected').val();
                current_study_program_id = $('#study_id option:selected').attr("program_id");
            }
            //TODO: check if this is needed
            //save center_id and associated program id for the currently selected in the center id select control
            if ($('#center_id').length > 0) {
                current_center_id = $('#center_id option:selected').val();
                current_center_program_id = $('#center_id option:selected').attr("program_id");
            }

            //refresh filter's div with the received data
            $('#filters').html(data);

            //get width of the filter labels assigned to the currently selected report
            filter_label_width = $('#select_report :selected').attr('filter_label_width');
            //update all filter labels with the provided width
            $(".input-group-text[filter_label_width]").css("width",filter_label_width);

            $('[name="clear_text_btn"]').on('click', function(){
                $("#" + $(this).attr('clear_target')).val('');
            })

            //hide error message div
            $('#filter_err_msg').hide();
            //hide select report message div
            $('#select_report_msg').hide();
            //make sure that select report div is visible
            $('#select_report_div').show();
            //display filters
            $('#filters').show();


            on_program_change(); //register program id control event
            // on_filter_change(); //register filter change event
            on_run_report(); //register Run Report button click
            on_download_report(); //register Download Report button click

            init_multiselect ($('#center_ids'), 'Keep blank for All or Select...');
            // init_multiselect ($('#center_id'));

            //for first time on loading - hides/shows studies and/or centers based on the default program id selected
            run_select_control_validation($("#study_id"), $('#program_id').val());
            run_select_control_validation($("#center_id"), $('#program_id').val());
            run_select_control_validation($("#center_ids"), $('#program_id').val());


            //identify if any control filters were assigned to this reports
            run_on_load = $('#select_report :selected').attr('run_on_load');
            if (run_on_load !== undefined) {
                //if run_on_load attribut is present, run report immediately after loading filters
                $("#run_report").click();
            }

            // onchange events to disable "Reload report" button if any of the filters got changed
            $("#program_id").change(function () {
                disable_reload_report_button();
            })
            $("#study_id").change(function () {
                disable_reload_report_button();
            })
            $("#center_id").change(function () {
                disable_reload_report_button();
            })
            $("#center_ids").change(function () {
                disable_reload_report_button();
            })
            $("#dataset_type_id").change(function () {
                disable_reload_report_button();
            })
            $("#sample_ids").change(function () {
                disable_reload_report_button();
            })
            $("#aliquot_ids").change(function () {
                disable_reload_report_button();
            })

          }
        })
        .fail(function(response, status) {
            err_html = response.responseText;
            // err_status_num = response.status;

            $('#filter_err_msg').html(err_html);
            $('#filter_err_msg').show();

            $('#select_report_msg').show();
            $('#select_report').prop('selectedIndex', 0);   //.val([]);
            $('#select_report_div').show();

            $('#filters').hide();
        });
    });

    // var search_box_event = function (){
    //     $(".multiselect-container > div > input").keyup(function(){
    //         console.log('keyup');
    //     });
    // }

    var init_multiselect = function (select_ctr, non_selected_text){
        if (select_ctr.length > 0) {
            if (select_ctr.attr('multiple') == 'multiple') {
                select_ctr.multiselect({
                    buttonWidth: '100%',
                    maxHeight: 250,
                    includeResetOption: true,
                    includeResetDivider: true,
                    numberDisplayed: 2,
                    resetText: "Clear all selected options",
                    // enableFiltering: true,
                    // enableCaseInsensitiveFiltering: true,
                    // includeFilterClearBtn: true,
                    // includeSelectAllOption: true,
                    nonSelectedText: non_selected_text, //'Keep blank or Choose... ',
                    selectedClass: 'active multiselect-selected'
                    // onDeselectAll: function() {
                    //     alert('onDeselectAll triggered!');
                    // },
                    , onChange: function (element, checked) {
                        // console.log($(".multiselect-container > button.disabled"));
                        // console.log();
                        $(".multiselect-container > button.disabled").hide();
                    }
                });

                //adjust height of the multiselect button after it was rendered
                // $("#center_id + div").css("height", "100%");
                select_ctr.siblings("div").css("height", "100%");
            }
        }
    }

    var init_datepicker = function (){
          // if desktop device, use DateTimePicker
          $("[datepicker]").datetimepicker({
            useCurrent: false,
            format: "L",
            showTodayButton: true,
            icons: {
              next: "fa fa-chevron-right",
              previous: "fa fa-chevron-left",
              today: "todayText"
            }
          });
          // $("#timepicker").datetimepicker({
          //   format: "LT",
          //   icons: {
          //     up: "fa fa-chevron-up",
          //     down: "fa fa-chevron-down"
          //   }
          // });
    }

    on_run_report_click = function (dummy, column_filters = false) {
            //$("#program_id").on('change', function () {
            $('#div_report').hide();
            $('#loader').show();

            var i;

            if (column_filters && $("[data-column-name]").length > 0) {
                // console.log(collect_report_column_filters());
                column_report_filters = collect_report_column_filters();
            } else {
                column_report_filters = "";
            }

            main_filters = collect_main_filters();
            main_filters['column_report_filters']= column_report_filters; // add additional value to be send to the server

            $.post("/get_report_data",
                main_filters,
                function (data, status) {
                    $('#loader').hide();
                    $('#div_report').html(data);
                    $('#div_report').show();
                    var mytable = data_table();
                    mytable.buttons()
                        .container()
                        .appendTo( '#report_wrapper .col-md-6:eq(0)' );
                    on_reload_report_with_filters(); //register Reload Report button


                    $("#copySelectionButton").click(function () {
                        copy_selection ('', mytable);
                    })

                })
                .fail(function(response, status) {
                        err_html = response.responseText;
                        $('#loader').hide();
                        $('#div_report').html(err_html);
                        $('#div_report').show();
                }
            );
        }

    on_download_report_click = function () {
            $('#div_report').hide();
            $('#loader').show();

            var i;

            main_filters = collect_main_filters(); // get values of all main filters
            main_filters['get_csv_file_only']= 'yes'; // add additional value to be send to the server

            $.post("/get_report_data",
                main_filters,
                function (data, status) {
                    $('#loader').hide();
                    $('#div_report').show();
                    // console.log(data['file_name']);
                    // console.log(data['csv']);
                    downloadCSV(data['csv'], data['file_name'])
                })
                .fail(function(response, status) {
                        err_html = response.responseText;
                        $('#loader').hide();
                        $('#div_report').html(err_html);
                        $('#div_report').show();
                }
            );
        }

    var downloadCSV = function(csvStr, file_name) {
        var hiddenElement = document.createElement('a');
        hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csvStr);
        hiddenElement.target = '_blank';
        hiddenElement.download = file_name;
        hiddenElement.click();
    }

    var copy_selection = function (dummy, mytable) {

        // mytable.cells( { selected: true } )[0].forEach((element, index) => console.log(element, mytable.cells({ selected: true }).data()[index]) );
        // console.log(mytable.cells({ selected: true })[0])
        // console.log ('In copy_selection function!')

        cell_delim = "\t"
        row_delim = "\r\n"

        col_min = 0
        for (i = 0; i < mytable.cells( { selected: true } )[0].length; i++) {
                element = mytable.cells({ selected: true })[0][i]
                // console.log(col_min, element["column"], element["row"], mytable.cells({ selected: true }).data()[i])
                if (col_min == 0 || col_min > element["column"]) {
                    col_min = element["column"];
                }
            }
        // console.log(col_min);

        // testString = mytable.cells({ selected: true }).data()[0];
        selection_str = '';
        for (i = 0; i < mytable.cells( { selected: true } )[0].length; i++) {
            cur_col = mytable.cells({ selected: true } )[0][i].column;  //current column #
            cur_row = mytable.cells({ selected: true } )[0][i].row;  //current row #

            if (i==0) {
                // processing the first cell
                if (cur_col > col_min) {
                    for (j = 1; j <= cur_col - col_min; j++) {
                        selection_str += cell_delim
                    }
                }
            }
            else {
                // process all other cells
                prev_row = mytable.cells({selected: true})[0][i - 1].row;
                if (cur_row > prev_row) {
                    // change of row is identified
                    for (r = 1; r <= cur_row - prev_row; r++) {
                            // add row delimiter for each row identified as difference between these neighbour cells
                            selection_str += row_delim
                        }
                    // selection_str += row_delim  // add row delimiter

                    // check if the first column of the new row > col_min and add cell delimiters if needed
                    if (cur_col > col_min) {
                        for (j = 1; j <= cur_col - col_min; j++) {
                            selection_str += cell_delim
                        }
                    }
                }
                else {
                    cell_diff = mytable.cells({selected: true})[0][i].column - mytable.cells({selected: true})[0][i - 1].column
                    for (k = 1; k <= cell_diff; k++) {
                            selection_str += cell_delim
                        }
                }
            }
            // add the cell value to the string
            selection_str += mytable.cells({selected: true}).data()[i];
        }

        // console.log(selection_str)

        // set global toastr properties (reference: https://github.com/CodeSeven/toastr)
        toastr.options = {
          "closeButton": false,
          "debug": false,
          "newestOnTop": false,
          "progressBar": true,
          "positionClass": "toast-bottom-right",
          "preventDuplicates": false,
          "onclick": null,
          "showDuration": "300",
          "hideDuration": "1000",
          "timeOut": "5000",
          "extendedTimeOut": "1000",
          "showEasing": "swing",
          "hideEasing": "linear",
          "showMethod": "fadeIn",
          "hideMethod": "fadeOut"
        }
        if (selection_str.length > 0) {
            // copy prepared string to clipboard
            copy_outcome = copyToClipboard(selection_str);
            if (copy_outcome){
                toastr.success('Selection was copied to clipboard.');
            }
            else {
                toastr.error('Error while copying to clipboard!')
            }
        }
        else {
            toastr.warning('No selection was detected, nothing was copied.', '', {timeOut: 10000})
        }
    }

    var copyToClipboard = function(textToCopy){
        // navigator clipboard api needs a secure context (https)
        if (navigator.clipboard && window.isSecureContext) {
            // navigator clipboard api method'
            return navigator.clipboard.writeText(textToCopy);
        } else {
            // text area method
            let textArea = document.createElement("textarea");
            textArea.value = textToCopy;
            // make the textarea out of viewport
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            // textArea.style.left = "10px";
            // textArea.style.top = "200px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                var outcome = document.execCommand('copy');
            } catch (err) {
                outcome = false;
            }
            textArea.remove();
            return outcome;
        }
    }

    //declare onClick event for Run Report button
    var on_run_report = function() {
        $("#run_report").click(on_run_report_click);
    }

    //declare onClick event for Reload Report With Column Filters
    var on_reload_report_with_filters = function (){
        if($("#reload_report_with_filters") !== undefined) {
            $("#reload_report_with_filters").click(function () {
                on_run_report_click('', true);
            })

            //initiate popover next to the reload button
            enable_popover('Reload Current Report',
                'Reload the current report applying provided column\'s filters in addition to main filters to limit the number of returned rows',
                $("#reload_report_popover"));
                }
    }

    var disable_reload_report_button = function(){
        if($("#reload_report_with_filters").length != 0) {
            // disable reload button
            $("#reload_report_with_filters").attr('disabled', '');
            //initiate popover next to the reload button
            enable_popover('Reload Current Report - Disabled',
                'Reload functionality was disabled due to changes of the main filters. Please rerun the whole report once again.',
                $("#reload_report_popover"));
        }
    }

    //declare onClick event for Download Report button
    var on_download_report = function() {
        $("#download_report").click(on_download_report_click);
    }

    on_filters_hide_click = function () {
        $('#sidebarMenu').removeClass('show');
        $('#sidebarMenu_minimized').addClass('show');
        $('.main_area').removeClass('px-4');
        $('.main_area').addClass('px-2');
    }

    on_filters_show_click = function () {
        $('#sidebarMenu').addClass('show');
        $('#sidebarMenu_minimized').removeClass('show');
        $('.main_area').removeClass('px-2');
        $('.main_area').addClass('px-4');
    }

    //register on click events to hide/show filters
    $("#filters_hide").click(on_filters_hide_click);
    $("#filters_show").click(on_filters_show_click);

    var collect_multiselect_values = function(multi_ctrl_id){
        var sel_centers_arr = [];
        ctrl_id = '#' + multi_ctrl_id
        if ($(ctrl_id)) {
                if ($(ctrl_id +' option:selected').length > 0) {
                    //collect one or more selected centers from the multi-select control
                    for (i = 0; i < $(ctrl_id + ' option:selected').length; i++) {
                        sel_centers_arr[i] = $(ctrl_id + '  option:selected')[i].value;
                    }
                    // return sel_centers_arr.join();
                } else {
                    //if no selected centers available, collect all not disabled centers and pass them as the selected ones
                    for (i = 0; i < $(ctrl_id + ' option[disabled!="disabled"]').length; i++) {
                        sel_centers_arr[i] = $(ctrl_id + ' option[disabled!="disabled"]')[i].value;
                    }
                    // return sel_centers_arr.join();
                }
            }
        else {
            // return sel_centers_arr.join();
        }
        return sel_centers_arr.join();
    }

    // collect values of all main filters
    var collect_main_filters = function(){
        main_filters =
            {
                report_id: $('#select_report').val() ? $('#select_report').val() : "",
                program_id: $('#program_id').val() ? $('#program_id').val() : "",
                study_id: $('#study_id option:selected').val(),  //sel_study,
                center_id: $('#center_id option:selected').val(),
                center_ids: collect_multiselect_values ('center_ids'),
                aliquot_ids: $('#aliquot_ids').val() ? $('#aliquot_ids').val() : "",
                sample_ids: $('#sample_ids').val() ? $('#sample_ids').val() : "",
                dataset_type_id: $('#dataset_type_id').val() ? $('#dataset_type_id').val() : "",
            };
        return main_filters;
    }

    // collect report column filters
    var collect_report_column_filters = function(){
        // removes divisions containing copies of the column's filter input controls that are managed by DataTable
        // all controls being removed are not used after the Datatable was rendered, however they have duplicated
        // attribute names to the actual column's search controls that complicates working with the latest
        $(".dataTables_sizing").remove();

        filters=[];
        for (i = 0; i < $("[data-column-name]").length; i++) {
            flt_dict={};
            flt_name = $("[data-column-name]")[i].getAttribute('data-column-name');
            flt_value = $("[data-column-name]")[i].value;
            flt_dict[flt_name] = flt_value;
            filters.push(flt_dict);
        }
        return JSON.stringify(filters);
    }

    // assign report column filters on load; it is used when report filters were already applied to the dataset
    // on server side and now just need to be shown on UI
    var assign_report_filters = function(){
        filters_str = $("#column_report_filters").text(); // get list of filters from a control
        if (Boolean(filters_str)) { // if list is not empty proceed here
            filters = JSON.parse(filters_str);
            // console.log(filters)
            // console.log(Array.isArray(filters))
            if (Array.isArray(filters)) {
                for (i = 0; i < filters.length; i++) {
                    for ([flt_name, flt_value] of Object.entries(filters[i])) {
                        $("[data-column-name='" + flt_name + "']").val(flt_value);
                    }
                }
            }
        }
    }

    //declare onChange event for program_id control
    var on_program_change = function() {
        $('#program_id').on('change', function () {
            run_select_control_validation($("#study_id"), this.value);
            run_select_control_validation($("#center_id"), this.value);
            run_select_control_validation($("#center_ids"), this.value);
        });
    }

    var run_select_control_validation = function(select_ctr, cur_parent_id){
        if (select_ctr.length > 0) {
            if (select_ctr.attr('multiple') == 'multiple') {
                validate_multiselect_control(select_ctr, cur_parent_id)
            }
            else {
                validate_select_control(select_ctr, cur_parent_id, true, true)
            }
        }
    }

    var validate_multiselect_control = function(select_ctr, cur_parent_id){
        //find all buttons (with class disabled) for the current select_ctr, and make them visible
        select_ctr.siblings().find(".multiselect-container").children(".multiselect-container > button.disabled").show();
        validate_select_control(select_ctr, cur_parent_id);
        select_ctr.multiselect('refresh'); //referesh multiselect control
        //hide all disabled options of the multiselect control
        select_ctr.siblings().find(".multiselect-container").children(".multiselect-container > button.disabled").hide();
    }

    var validate_select_control = function(select_ctr, cur_parent_id, hide_disabled_options, select_first_option){
        if (hide_disabled_options !== undefined && hide_disabled_options){
            select_ctr.find('option[disabled="disabled"]').show();
        }
        //remove "disabled" attribute for any options of the select_ctr
        select_ctr.find("[parent_id]").removeAttr("disabled");
        // set disabled attribute back for options where parent id matches cur_parent_id
        select_ctr.find("[parent_id]").not("[parent_id="+ cur_parent_id + "]").attr("disabled", true);
        if (hide_disabled_options !== undefined && hide_disabled_options){
            select_ctr.find('option[disabled="disabled"]').hide();
        }

        select_ctr.val(''); //clear the current value

        if (select_first_option !== undefined && select_first_option){
           $(select_ctr.find('option[disabled!="disabled"]')[0]).attr("selected", "selected");
        }
    }

    var data_table = function() {
        if ($('#max_rows_msg').length) {
            dt_height_offset_value = 350;
        }
        else{
            dt_height_offset_value = 280
            }
        return $('#report').DataTable({
            //TODO: try this dome setting, should bring search boxes on top of the table -> dom = 'lfBtip'
            //<'col-sm-12 col-md-1'l><'col-sm-12 col-md-1'>
            dom: "<'row'<'col-sm-12 col-md-8'B><'col-sm-12 col-md-1'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            buttons: [
                {
                    extend: 'copyHtml5',
                    text: 'Copy Filtered Data'
                },
                {
                    extend: 'csvHtml5',
                    text: 'CSV Filtered Data'
                },
                {
                    text: 'Copy Selected',
                    action: function ( e, dt, node, config ) {
                        $("#copySelectionButton").click();
                    }
                },
                'colvis',
            ],

            //dom: "lfBtip",
            // pageLength:     25, // default page length
            // fixedHeader:    true, // preserves header row
            keys:           true, // adds excel like filling allowing selecting current cell
            select: {
                style: 'os',
                items: 'cell'
            },
            // following group of variables defines scrolling functionality
            scrollY:        calc_datatable_height(dt_height_offset_value), //600 //'70vh', //
            // scrollx:        true,
            scrollResize:   true,
            scrollCollapse: true,
            paging: false,
            // lengthChange: false,
            // pageLength: 50,

            deferRender: true,
            // scroller:       true,
            // scroller: {
            //     loadingIndicator: true
            // },
            initComplete: function () {
                var table = this; //reference to the DataTable

                // $('.dataTables_scrollBody').height(calc_datatable_height()) //set scroller body height to match the size of the window
                //adjust_scrollbody_height_to_match_datatable(); //adjust scroller body height to match datatable height (needed for small datasets)
                // adjust_scrollbody_width_to_fit_window(); //adjust scroller body width to match the width of the window

                //setup events handler for all controls with "data-column-name" attribute name
                $("[data-column-name]").on('keyup change clear', function () {
                    //console.log($(this).attr("data-column-name") + " : " + $(this).val());
                    //console.log(table.api().columns());
                    table.api()
                        .columns($(this).attr("data-column-id"))
                        .search($(this).val())
                        .draw();
                });

                    assign_report_filters();

                    $(window).on('resize', function () {
                        //adjust datatable scroller body on windows resize
                        $('.dataTables_scrollBody').height(calc_datatable_height()) //set scroller body height to match the height of the window
                        //adjust_scrollbody_height_to_match_datatable(); //adjust scroller body height to match datatable height (needed for small datasets)
                        // adjust_scrollbody_width_to_fit_window(); //adjust scroller body width to match the width of the window
                    });

            }
        });
    }

    //not in use currently
    //calculates datatable height for setting up scroller's height
    var calc_datatable_height = function(offset_val) {
        offset_val = offset_val || 280  // set default value if value was not provided
        if (jQuery(window).height() <= offset_val){
            //if windows height is > offset_val, reset it to 0
            offset_val = 0;
        }
        return Math.round(jQuery(window).height() - offset_val);
    };

    // checks if the datatable height is less then the scroller's body height and adjusts scroller to match the table height
    var adjust_scrollbody_height_to_match_datatable = function() {
        //get heights of the datatable and scroller
        scrollbody_height = $('.dataTables_scrollBody').height();
        datatable_height = Math.ceil($("table#report").height());
        //adjust scroller body height if it is > datatable height
        if (datatable_height < scrollbody_height){
          $('.dataTables_scrollBody').height(datatable_height);
        }
    };

    var adjust_scrollbody_width_to_fit_window = function(offset_val) {
        offset_val = offset_val || 75  // set default value if value was not provided
        //get width of the the main components
        //$('.dataTables_scroll').width(jQuery(window).width() - $('#sidebarMenu').width() - 100)
        window_width = jQuery(window).width();
        sidebar_width = $('#sidebarMenu').width();
        //adjust scroller body height if it is > datatable height
        if (window_width > (sidebar_width + offset_val)){
          $('.dataTables_scroll').width(window_width - sidebar_width - offset_val);
        }
    };


    //assign current value of the dropdown to the tool tip
    var assign_selected_option_to_tooltip = function(control, selected_option){
        control.prop('title', selected_option.text());
    }

    //run assignment of the tooltip for select_report on the initial load
    assign_selected_option_to_tooltip ($('#select_report'), $('#select_report :selected'));

    // $(function () {
    //   $('[data-toggle="popover"]').popover();
    // })

    // $(function () {
    //   $('#report_popover').popover({
    //     container: 'body'
    //   })
    // })

    //popover enabling function
    var enable_popover = function(title, content, popover_ctrl) {
        //$('#report_popover').popover('dispose');

        if (popover_ctrl === undefined){
            popover_ctrl = $('#report_popover') //assign default control if nothing was sent as a parameter
        }

        popover_ctrl.popover('show')
            .popover('dispose')
            .popover({
                container: ' body',
                // trigger: 'hover',
                trigger: 'focus',
                //html: true,
                placement: 'right',
                title: title, //'Select Report',
                content: content //'Select a report from the list. Once one is selected, this help window will display additional info about the selected report.',
            })//.popover("show");

        /*
         * The following two handlers provide the functionality of a "click" trigger
         * Once the popover is fully shown we bind an event listener to the button click
         * on button click the focus is blured thus closing the popover.
         * On hiding the popover we unbind the event listener from the button
         */
        popover_ctrl.on('shown.bs.popover', function(){
            //onclick event to close popover
            popover_ctrl.on('click', function() {
                // console.log('click');
                $(this).off('click');
                popover_ctrl.blur();
            });
            //onkeyup event to close popover
            $(document).keyup(function (e) {
                if (e.key === "Escape") { // escape key maps to keycode `27`
                    // console.log('escape');
                    popover_ctrl.blur();
                }
            });
            // $(this).popover("hide");
        });

        popover_ctrl.on('hide.bs.popover', function(){
            $(document).off('keyup');
        });

    }

    //initiate popover
    enable_popover('Select Report',
        'Select a report from the list. Once one is selected, this help window will display additional info about the selected report.');

} );