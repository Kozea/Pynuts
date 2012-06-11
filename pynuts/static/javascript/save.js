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

function save (divs, span_containers, message, url, ok_callback, error_callback) { 
    var data = [];
    $.each(divs, function () {
        if($(this).attr('data-hash') != hashCode($(this).html())) {
            data.push({
                "part": $(this).attr('data-part'),
                "document_type": $(this).attr('data-document-type'),
                "document_id": $(this).attr('data-document-id'),
                "version": $(this).attr('data-document-version'),
                "content": $(this).html()
            });
        }
    });
    $.each(span_containers, function () {
        var spans = $(this).find('span[contenteditable]');
        var values = [];
        $.each(spans, function () {
             values.push($(this).html());
        })
        data.push({
            "part": $(this).attr('data-part'),
            "document_type": $(this).attr('data-document-type'),
            "document_id": $(this).attr('data-document-id'),
            "version": $(this).attr('data-document-version'),
            "content": JSON.stringify(values)
        });
    });
    // Make ajax
    $.ajax({
        url: url,
        data: JSON.stringify({'data': data, 'message': message}),
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
                ok_callback();
            } else {
                error_callback();
            }            
        }
    });
}
	
