(function($) {
    let reorder_the_list = function() {
        let $items = $("ul.listing > li")
        $items.each( function ( index, el ) {
            let $el = $(el);

            let $label = $el.find('label')
            let $input = $el.find('input[type=text]')
            let $deleteBtn = $el.find('.delete-btn')

            $label.attr('for', "fact_list__" + index);
            $label.html(index + ":");

            $input.attr('id', "fact_list__" + index);
            $input.attr('name', "fact_list__" + index);

            $deleteBtn.attr('id', "delete_fact_list__" + index);

            $(".form-row.field-fact_list ul").last().find("input:first").focus()
        })
    };

    let add_empty = function () {
        let new_item = $("<ul>", {class: "listing"})
            .append(
                $("<li>")
                    .append($("<label>"))
                    .append($("<input>", {type: "text", value: ""}))
                    .append($("<input>", {type: "button", class: "delete-btn", value: "delete"}))
            );

        new_item.insertBefore($("#add_new"));
        reorder_the_list();
    };

    $(document).ready(function(event){
        $("#add_new").on('click', function(){
            add_empty();
        });

        $("div.field-fact_list").on('click', '.delete-btn', function(event){
            let $item = $(event.target).closest('li');
            let conf = confirm("Do you want to delete?")
            if(!conf) { return; }
            $item.remove();
            reorder_the_list();
        });

        $('form').submit(function( event ){
            let form = this;
            let list_inputs = $(".field-fact_list").find("input:text");
            event.preventDefault();

            list_inputs.each(function(index, el){
                let $el = $(el);
                $el.val($el.val().trim());
            })

            list_inputs.filter(function(){
                return $(this).val() === ""; }).remove()

            setTimeout(function(){
                form.submit();
            }, 50);
        });
    });
})(django.jQuery);
