function newtab(util, hostname) {
  var id = idgen();
  $('#hostTab').append('<li class="nav-item" id="' + id + '-li"><a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false"><button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button><button class="refreshtab" type="button" onclick="document.getElementById(\'frame-' + id + '\').src += \'\';document.getElementById(\'fframe-' + id + '\').src += \'\';">⟳</button>' + hostname + '</a></li>');
  $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
  document.getElementById(id + "-tab").click();
 sleep(250).then(() => {
  $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/' + util + '"></iframe>');
  });
};

$(document).ready(function() {
  $('[data-toggle=offcanvas]').click(function() {
      $('.row-offcanvas').toggleClass('active');
  });
});