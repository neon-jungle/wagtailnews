function initModal(modal) {
	var query = $("#id_q");
	var type = $("#id_type");

	function ajaxifyLinks(context) {
		$('a.newsitem-choice', modal.body).click(function() {
			modal.loadUrl(this.href);
			return false;
		});

		$('.pagination a', context).click(function() {
			var page = this.getAttribute('data-page');
			setPage(page);
			return false;
		});
	}

	var searchUrl = $('form.newsitem-search', modal.body).attr('action');

	function makeQueryData() {
		return {
			q: query.val(),
			type: type.val(),
			results: 'true',
		};
	}

	function search() {
		$.ajax({
			url: searchUrl,
			data: makeQueryData(),
			success: function(data, status) {
				$('#search-results').html(data);
				ajaxifyLinks($('#search-results'));
			}
		});
		return false;
	}

	function setPage(page) {
		var dataObj = makeQueryData();
		dataObj.p = page;

		$.ajax({
			url: searchUrl,
			data: dataObj,
			success: function(data, status) {
				$('#search-results').html(data);
				ajaxifyLinks($('#search-results'));
			}
		});
		return false;
	}

	$('form.newsitem-search', modal.body).submit(search);

	$('#id_q').on('input', function() {
		clearTimeout($.data(this, 'timer'));
		var wait = setTimeout(search, 50);
		$(this).data('timer', wait);
	});

	ajaxifyLinks(modal.body);
}
