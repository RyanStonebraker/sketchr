jQuery(document).ready(function ($) {
  $('body').on('change keyup keydown paste cut', 'textarea', function () {
          $(this).height(0).height(this.scrollHeight);
      }).find('textarea').change();
});
