function hashCode(string) {
    var hash = 0;
    if (string.length == 0) return hash;
    for (i = 0; i < string.length; i++) {
        char = string.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

function save (options) {
    //Params : divs, span_containers, url, message, ok_callback, error_callback, empty_callback
    var data = [];
    if (options.divs) {
        $.each(options.divs, function () {
            if($(this).attr('data-hash') != hashCode($(this).html())) {
                data.push({
                    "part": $(this).attr('data-part'),
                    "document_type": $(this).attr('data-document-type'),
                    "document_id": $(this).attr('data-document-id'),
                    "version": $(this).attr('data-document-version'),
                    "content": $(this).html()
                });
            }
            $(this).attr('data-hash', hashCode($(this).html()));
        });
    }
    if (options.span_containers) {
        $.each(options.span_containers, function () {
            var spans = $(this).find('span[contenteditable]');
            var values = [];
            $.each(spans, function () {
                values.push($(this).html());
            });
            data.push({
                "part": $(this).attr('data-part'),
                "document_type": $(this).attr('data-document-type'),
                "document_id": $(this).attr('data-document-id'),
                "version": $(this).attr('data-document-version'),
                "content": JSON.stringify(values)
            });
        });
    }

    // Check if contents is null
    if (data.length == 0) {
        if (options.empty_callback) options.empty_callback();
        return false;
    }

    // Make ajax
    if (options.message) {
        ajax_data = JSON.stringify({'data': data, 'message': options.message});
    }
    else {
        ajax_data = JSON.stringify({'data': data});
    }
    $.ajax({
        url: options.url,
        data: ajax_data,
        contentType: 'application/json',
        dataType: 'json',
        type: "POST",
        success: function(response){
            if(response && response.documents) {
                $.each(response.documents, function () {
                    var divs = $('#iframe').contents().find(
                        'div[contenteditable]' +
                        '[data-document-type="' + this.document_type + '"]' +
                        '[data-document-id="' + this.document_id + '"]'
                    );
                    divs.attr('data-document-version', this.version);
                });
                if (options.ok_callback) options.ok_callback();
            } else {
                if (options.error_callback) options.error_callback();
            }
        }
    });
}
