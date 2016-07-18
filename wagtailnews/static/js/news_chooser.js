function createNewsChooser(id) {
	var chooserElement = $('#' + id + '-chooser');
	var docTitle = chooserElement.find('.title');
	var input = $('#' + id);
	var editLink = chooserElement.find('.edit-link');
	if (NEWS_PK) {
		var newsChooser = "/admin/news/chooser/" + NEWS_PK + '/';
	} else {
		var newsChooser = "/admin/news/chooser/";
	}

	$('.action-choose', chooserElement).click(function() {
		ModalWorkflow({
			url: newsChooser,
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
		chooserElement.addClass('blank');
	});
}
