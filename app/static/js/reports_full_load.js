$(document).ready(function() {
    var table = $('#report').DataTable({
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
            })
        }
    });
} );