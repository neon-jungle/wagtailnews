function createNewsChooser(id, type) {
	var chooserElement = $('#' + id + '-chooser');
	var docTitle = chooserElement.find('.title');
	var input = $('#' + id);
	var editLink = chooserElement.find('.edit-link');
	var url = window.chooserUrls.newsChooser + '?type=' + type;

	$('.action-choose', chooserElement).click(function() {
		ModalWorkflow({
			url: url,
			responses: {
				newsItemChosen: function(newsData) {
					input.val(newsData.id);
					docTitle.text(newsData.string);
					chooserElement.removeClass('blank');
					editLink.attr('href', newsData.edit_link);
				}
			}
		});
	});

	$('.action-clear', chooserElement).click(function() {
		input.val('');
		docTitle.text('');
		chooserElement.addClass('blank');
	});
}
