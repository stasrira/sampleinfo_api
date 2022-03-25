$(document).ready(function() {

    //select_report onChange event
    $('#select_report').on('change', function () {

        //assign current report title to the header
        $('#report_title').text($('#select_report :selected').text())

        //assign current value to the tool tip
        assign_selected_option_to_tooltip ($('#select_report'), $('#select_report :selected'));

        //console.log($('#select_report :selected').attr('helptip'));
        enable_popover(
            $('#select_report :selected').attr('helptip').split("|")[0],
            $('#select_report :selected').attr('helptip').split("|")[1]
        );

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

            //display filters
            $('#filters').show();

            on_program_change(); //register program id control event
            // on_filter_change(); //register filter change event
            on_run_report(); //register Run Report button click

            init_multiselect ($('#center_ids'));
            // init_multiselect ($('#center_id'));

            // if ($('#center_ids[multiple="multiple"]').length > 0) {
            //     $('#center_ids').multiselect({
            //         buttonWidth: '100%',
            //         maxHeight: 250,
            //         includeResetOption: true,
            //         includeResetDivider: true,
            //         numberDisplayed: 2,
            //         resetText: "Clear all selected options",
            //         // enableFiltering: true,
            //         // enableCaseInsensitiveFiltering: true,
            //         // includeFilterClearBtn: true,
            //         // includeSelectAllOption: true,
            //         nonSelectedText: 'Keep blank or Choose... ',
            //         selectedClass: 'active multiselect-selected'
            //         // onDeselectAll: function() {
            //         //     alert('onDeselectAll triggered!');
            //         // },
            //         , onChange: function (element, checked) {
            //             // console.log($(".multiselect-container > button.disabled"));
            //             // console.log();
            //             $(".multiselect-container > button.disabled").hide();
            //         }
            //     });
            //
            //     //adjust height of the multiselect button after it was rendered
            //     $("#center_ids + div").css("height","100%");
            // }

            // if ($('#center_id[multiple="multiple"]').length > 0) {
            //     $('#center_id').multiselect({
            //         buttonWidth: '100%',
            //         maxHeight: 250,
            //         includeResetOption: true,
            //         includeResetDivider: true,
            //         numberDisplayed: 2,
            //         resetText: "Clear all selected options",
            //         // enableFiltering: true,
            //         // enableCaseInsensitiveFiltering: true,
            //         // includeFilterClearBtn: true,
            //         // includeSelectAllOption: true,
            //         nonSelectedText: 'Keep blank or Choose... ',
            //         selectedClass: 'active multiselect-selected'
            //         // onDeselectAll: function() {
            //         //     alert('onDeselectAll triggered!');
            //         // },
            //         , onChange: function (element, checked) {
            //             // console.log($(".multiselect-container > button.disabled"));
            //             // console.log();
            //             $(".multiselect-container > button.disabled").hide();
            //         }
            //     });
            //
            //     //adjust height of the multiselect button after it was rendered
            //     $("#center_id + div").css("height","100%");
            // }

            // //run assignment of the tooltip for pivot_by dropdown on the initial load of the filter
            // assign_selected_option_to_tooltip ($('#pivot_by'), $('#pivot_by :selected'));

            //TODO: check if this is needed
            //assign onChaneg event to pivot_by dropdown
            // $('#pivot_by').on('change', function () {
            //     assign_selected_option_to_tooltip ($('#pivot_by'), $('#pivot_by :selected'));
            // });

            //TODO: check if this is needed
            // //search box event registration
            // search_box_event ();

            //TODO: check if this is needed
            // initilalite datepicker plugin
            // init_datepicker();
            // });

            //for first time on loading - hides/shows studies based on the default program id selected
            //validate_studies($('#program_id').val()); //run this function for first time on loading

            // if ($("#study_id").length > 0){
            //     if ($('#study_id[multiple="multiple"]').length > 0) {
            //         validate_multiselect_control($("#study_id"), $('#program_id').val())
            //     }
            //     else {
            //         validate_select_control($("#study_id"), $('#program_id').val(), true)
            //     }
            //
            // }

            // if ($("#center_id").length > 0) {
            //     if ($('#center_id[multiple="multiple"]').length > 0) {
            //         validate_multiselect_control($("#center_id"), $('#program_id').val())
            //     }
            //     else {
            //         validate_select_control($("#center_id"), $('#program_id').val(), true)
            //     }
            // }

            //for first time on loading - hides/shows studies and/or centers based on the default program id selected
            run_select_control_validation($("#study_id"), $('#program_id').val());
            run_select_control_validation($("#center_id"), $('#program_id').val());
            run_select_control_validation($("#center_ids"), $('#program_id').val());

            //TODO: check if this is needed
            // //check if previously selected study_id can be selected again
            // if ($('#study_id').length > 0) {
            //     //if current study_id item belongs to the currently selected program_id
            //     if (current_study_program_id == $('#program_id').val()) {
            //         if ($('#study_id option[value = ' + current_study_id + ']').css('display') != 'none') {
            //             //if the option being selected is visible
            //             $('#study_id option[value = ' + current_study_id + ']').prop('selected', true);
            //         }
            //     }
            // }
            // if ($('#center_id').length > 0) {
            //     //if current center_id item belongs to the currently selected program_id
            //     if (current_center_program_id == $('#program_id').val()) {
            //         if ($('#center_id option[value = ' + current_center_id + ']').css('display') != 'none') {
            //             //if the option being selected is visible
            //             $('#center_id option[value = ' + current_center_id + ']').prop('selected', true);
            //         }
            //     }
            // }

          }
        });
    });

    // var search_box_event = function (){
    //     $(".multiselect-container > div > input").keyup(function(){
    //         console.log('keyup');
    //     });
    // }

    var init_multiselect = function (select_ctr){
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
                    nonSelectedText: 'Keep blank or Choose... ',
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

    //declare onChange event for any filter change
    var on_filter_change = function() {
        $("#filters :input").on('change', function () {
            //$("#program_id").on('change', function () {
            $('#div_report').hide();
            $('#loader').show();
            //$('#div_report').hide();
            //alert($('#study_id option:selected')); //$('#study_id')
            var sel_studies_arr = [];
            var sel_studies = '';
            var i;

            // $('#study_id option:selected').each(function() {
            //     sel_studies = sel_studies + (',' + this.value ? sel_studies : this.value)
            // })

            if ($('#study_id option:selected')) {
                for (i = 0; i < $('#study_id option:selected').length; i++) {
                    sel_studies_arr[i] = $('#study_id option:selected')[i].value;
                }
                sel_studies = sel_studies_arr.join();
            }
            //console.log('Selected studies-> ' + sel_studies);

            $.post("/get_report_data",
                {
                    report_id: $('#select_report').val() ? $('#select_report').val() : "",
                    program_id: $('#program_id').val() ? $('#program_id').val() : "",
                    //study_id: $('#study_id').val() ? $('#study_id').val() : "",
                    study_id: sel_studies,
                    aliquot_ids: $('#aliquot_ids').val() ? $('#aliquot_ids').val() : "",
                    date_from: $('#date_from').val() ? $('#date_from').val() : "",
                    date_to: $('#date_to').val() ? $('#date_to').val() : "",
                    pivot_by: $('#pivot_by').val() ? $('#pivot_by').val() : "",
                },
                function (data, status) {
                    $('#loader').hide();
                    $('#div_report').html(data);
                    $('#div_report').show();
                    var mytable = data_table();
                    mytable.buttons()
                        .container()
                        .appendTo( '#report_wrapper .col-md-6:eq(0)' );
                });
        });
    }

    //declare onChange event for any filter change
    var on_run_report = function() {
        $("#run_report").click(function () {
            //$("#program_id").on('change', function () {
            $('#div_report').hide();
            $('#loader').show();
            //$('#div_report').hide();
            //alert($('#study_id option:selected')); //$('#study_id')
            var sel_centers_arr = [];
            var sel_studies = '';
            var i;

            // $('#study_id option:selected').each(function() {
            //     sel_studies = sel_studies + (',' + this.value ? sel_studies : this.value)
            // })

            if ($('#center_ids option:selected')) {
                for (i = 0; i < $('#center_ids option:selected').length; i++) {
                    sel_centers_arr[i] = $('#center_ids option:selected')[i].value;
                }
                sel_centers = sel_centers_arr.join();
            }
            // console.log('Selected studies-> ' + sel_studies);  //TODO: remove this line after testing

            $.post("/get_report_data",
                {
                    report_id: $('#select_report').val() ? $('#select_report').val() : "",
                    program_id: $('#program_id').val() ? $('#program_id').val() : "",
                    //study_id: $('#study_id').val() ? $('#study_id').val() : "",
                    study_id: $('#study_id option:selected').value,  //sel_study,
                    center_id: $('#center_id option:selected').value,
                    center_ids: sel_centers,
                    aliquot_ids: $('#aliquot_ids').val() ? $('#aliquot_ids').val() : "",
                    sample_ids: $('#sample_ids').val() ? $('#sample_ids').val() : "",
                    dataset_type_id: $('#dataset_type_id').val() ? $('#dataset_type_id').val() : "",
                    // date_from: $('#date_from').val() ? $('#date_from').val() : "",
                    // date_to: $('#date_to').val() ? $('#date_to').val() : "",
                },
                function (data, status) {
                    $('#loader').hide();
                    $('#div_report').html(data);
                    $('#div_report').show();
                    var mytable = data_table();
                    mytable.buttons()
                        .container()
                        .appendTo( '#report_wrapper .col-md-6:eq(0)' );
                });
        });
    }

    //declare onChange event for program_id control
    var on_program_change = function() {
        $('#program_id').on('change', function () {
            run_select_control_validation($("#study_id"), this.value);
            run_select_control_validation($("#center_id"), this.value);
            run_select_control_validation($("#center_ids"), $('#program_id').val());
        });
    }

    var run_select_control_validation = function(select_ctr, cur_parent_id){
        if (select_ctr.length > 0) {
            if (select_ctr.attr('multiple') == 'multiple') {
                validate_multiselect_control(select_ctr, cur_parent_id)
            }
            else {
                validate_select_control(select_ctr, cur_parent_id, true)
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

    var validate_select_control = function(select_ctr, cur_parent_id, hide_disabled_options){
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
    }

    var data_table = function() {
        return $('#report').DataTable({
            //TODO: try this dome setting, should bring search boxes on top of the table -> dom = 'lfBtip'
            dom: "<'row'<'col-sm-12 col-md-1'l><'col-sm-12 col-md-1'><'col-sm-12 col-md-3'B><'col-sm-12 col-md-1'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            buttons: [
                'copyHtml5', 'csvHtml5', 'colvis'
            ],
            //dom: "lfBtip",
            "pageLength": 10,
            initComplete: function () {
                // Apply the search
                var table = this; //reference to the DataTable
                //setup events handler for all controls with "data-column-name" attribute name
                $("[data-column-name]").on( 'keyup change clear', function() {
                    //console.log($(this).attr("data-column-name") + " : " + $(this).val());
                    //console.log(table.api().columns());
                    table.api()
                        .columns($(this).attr("data-column-id"))
                        .search( $(this).val())
                        .draw();
                });

            }
        });
    }

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
    var enable_popover = function(title, content) {
        //$('#report_popover').popover('dispose');
        $('#report_popover').popover('show')
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
        $('#report_popover').on('shown.bs.popover', function(){
            //onclick event to close popover
            $('#report_popover').on('click', function() {
                console.log('click');
                $(this).off('click');
                $('#report_popover').blur();
            });
            //onkeyup event to close popover
            $(document).keyup(function (e) {
                if (e.key === "Escape") { // escape key maps to keycode `27`
                    console.log('escape');
                    $('#report_popover').blur();
                }
            });
            // $(this).popover("hide");
        });

        $('#report_popover').on('hide.bs.popover', function(){

            $(document).off('keyup');
        });

    }

    //initiate popover
    enable_popover('Select Report',
        'Select a report from the list. Once one is selected, this help window will display additional info about the selected report.');

} );