 function appendtab(id, util) {
     $('#hostTab').append('<li class="nav-item" id="' + id + '-li"><a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false"><button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button><button class="refreshtab" type="button" onclick="updatetab(\''+id+'\', \''+util+'\')">⟳</button>' + util + '</a></li>'
     );
 }
 function appendform(id, util) {
     $('#'+id).append('<form onsubmit="openutil(\''+id+'\', \''+util+'\')">        <div class="form-group">          <label for="Arguments">Tool arguments:</label>          <input type="text" class="form-control" id="'+id+'-arg" placeholder="--arg1=value1 --arg2=value2 --debug">        </div>        <button type="button" class="btn btn-primary" onclick="openutil(\''+id+'\', \''+util+'\')" style="width: 10%;">Run</button>        </form>')
 }
 function appendcontent(id, util) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     appendform(id, util);
     $.ajax({type : 'GET', url: "/help/"+util, dataType : 'text',
         success: function (data) {
         $('#'+id).append('<pre>'+data+'</pre>')
         }
     });
 }
 function appendframe(id, util) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     sleep(250).then(() => {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/'+util+'/"></iframe>');
     });
     }
 function openutil(id, util) {
     var args = document.getElementById(id+'-arg').value;
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/'+util+'/'+args+'"></iframe>');
     sleep(250).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function newtab(util) {
     var id = idgen();
     appendtab(id, util);
     appendcontent(id, util);
 };
 function newdirecttab(util) {
     var id = idgen();
     appendtab(id, util);
     appendframe(id, util);
 };
 function updatetab(id, util) {
     $('#'+id).html('')
     appendcontent(id, util);
 };

 $(document).ready(function() {
     $('[data-toggle=offcanvas]').click(function() {
         $('.row-offcanvas').toggleClass('active');
     });
 });