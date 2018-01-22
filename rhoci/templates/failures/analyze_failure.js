function analyze_failure(elem, job, build) {
		var $this = $(elem);
		$this.text('Analyzing...Please Wait');

  $.ajax({
    type:"GET",
    dataType: "json",
    data: {'job': job, 'build': build},
    url: "{{ url_for('builds.analyze_failure') }}",
    success: function(response){
		  $this.text(response.failure_name);
      $this.attr('onclick','show_failure(\''+ job + '\', \'' + build + '\')');
    }
  });

}
