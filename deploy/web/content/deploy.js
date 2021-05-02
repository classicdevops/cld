 function appendtab(id, deploy, deploytype) {
     $('#hostTab').append('<li class="nav-item" id="' + id + '-li">\
         <a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false">\
         <button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button>\
         <button class="refreshtab" type="button" onclick="updatetab(\''+id+'\', \''+deploy+'\', \''+deploytype+'\')">⟳</button>' + deploy + '\
         </a></li>'
     );
 }
 function appenddeploytab(id, util) {
     $('#hostTab').append('<li class="nav-item" id="' + id + '-li"><a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false"><button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button><button class="refreshtab" type="button" onclick="updatedeploytab(\''+id+'\', \''+util+'\')">⟳</button>' + util + '</a></li>'
     );
 }
 function appendfilecontent(id, deploy, deploytype, filecontent, filenamestr) {
     var filename = filenamestr.replace(' ', '_')
     if (filename == "script") { expanded = "true" ; collapsed = "" ; toggle = " in" ; } else { expanded = "false" ; collapsed = " collapsed" ; toggle = "" ; };
     $('#'+id+'-accordion').append('<div id="panel'+filename+id+'" class="panel panel-default'+collapsed+'">\
         <div class="panel-heading" data-toggle="collapse" data-parent="#'+id+'-accordion" href="#collapse'+id+filename+'" aria-expanded="'+expanded+'" style="cursor:pointer;">\
           <h4 class="panel-title">\
             <a data-toggle="collapse" data-parent="#'+id+'-accordion" href="#collapse'+id+filename+'">\
                     file: '+filenamestr+'</a>\
             </h4>\
             <button class="btn btn-danger dpl_del_file_btn" onclick="deletedeployfile(\''+id+'\', \''+deploytype+'\', \''+deploy+'\', \''+filenamestr+'\')">✖</button>\
             <div style="float: right;margin: -17px 15px -20px 0px;">\
             <input id="link'+id+filename+'" class="prelink" value="https://'+cld_domain+'/api/deploy/'+deploytype+'/'+deploy+'/'+filenamestr+'?hash='+CryptoJS.MD5(deploytype+deploy+filenamestr+userapitoken).toString()+'" readonly></div>\
         </div>\
         <div id="collapse'+id+filename+'" class="panel-collapse collapse'+toggle+'">\
             <div class="panel-body aceinit">\
         <pre id="'+filename+id+'">'+escapeHtml(filecontent)+'</pre>\
         </div></div></div>');
     $('#link'+id+filename)[0].style.width = (($('#link'+id+filename)[0].value.length) * 5.63) + 'px';
     ace.edit(filename+id, {
         theme: "ace/theme/monokai",
         keyboardHandler: "ace/keyboard/sublime",
         foldStyle: "markbeginend",
         mode: "ace/mode/sh",
         maxLines: 40,
         minLines: 5,
         wrap: true,
         showPrintMargin: false,
         autoScrollEditorIntoView: true,
         highlightSelectedWord: true
     });
     var editor = [];
     editor[filename+id] = ace.edit(filename+id);
     editor[filename+id].renderer.setScrollMargin(10, 15, 0, 0);
     $('#'+id+'-form').append('<textarea name="'+filenamestr+'" id="textarea'+filename+id+'"></textarea>')
     $('#textarea'+filename+id).val(editor[filename+id].getSession().getValue());
     editor[filename+id].getSession().on('change', function () {
        $('#textarea'+filename+id).val(editor[filename+id].getSession().getValue());
     });
     var stopClickEventPropagation = function (e) {
         e.stopPropagation();
         e.target.select();
         document.execCommand('copy');
     };
     $('#link'+id+filename).on('click', stopClickEventPropagation);
 }
 function deletedeployfile(id, deploytype, deploy, filename) {
     $.ajax({type : 'GET', url: '/deploy/delete/'+deploytype+'/'+deploy+'/'+filename, dataType : 'text',
         success: function (data) {
             document.getElementById("panel"+filename.replace(' ', '_')+id).remove();
             document.getElementById("textarea"+filename.replace(' ', '_')+id).remove();
         }
     });
 }
 function appendcontent(id, deploy, deploytype) {
     String.prototype.capitalize = function() {
         return this.charAt(0).toUpperCase() + this.slice(1);
     }
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     $('#'+id).append('<div class="panel-group" id="'+id+'-accordion"></div>')
     deploytypestr = deploytype.slice(0, -1);
     $('#'+id+'-accordion').append(deploytypestr.capitalize()+': '+deploy+'<br><br>')
     $('#'+id+'-accordion').append('\
         <button type="button" class="btn btn-primary" onclick="savedeploy(\''+id+'\', \''+deploy+'\', \''+deploytype+'\')" id="'+id+'-form-button" style="width: 10%; min-width: 120px;">Save '+deploytypestr+'</button>  \
         <button type="button" class="btn btn-primary" onclick="rundeploy(\''+id+'\', \'--'+deploytypestr+'='+deploy+'\')" style="width: 10%; min-width: 120px;">Run '+deploytypestr+'</button>  \
         <button type="button" class="btn btn-danger" onclick="deletedeploy(\''+id+'\', \''+deploytype+'\', \''+deploy+'\')" style="width: 10%; min-width: 120px;">Delete '+deploytypestr+'</button>\
         <form style="display: -webkit-inline-box;margin-left: 5;" onsubmit="createfile(\''+id+'\', \''+deploy+'\', \''+deploytype+'\');return false;">\
         <input type="text" class="form-control" id="'+id+'-inputfilename" placeholder="New file name" style="width: 45%;padding-top: 3;" required>\
         <button type="submit" class="btn btn-primary" style="margin-left: -5; border-radius: 0px 4px 4px 0px;">Create</button></form>\
         <br><br>')
     $('#'+id+'-accordion').append('<form id="'+id+'-form" style="display: none;"></form>')
     $.ajax({type : 'GET', url: "/deploy/"+deploytype+"/"+deploy+"/files", dataType : 'json',
         success: function (objfiles) {
             for (filename in objfiles) {
                 if (filename != ""){
                     appendfilecontent(id, deploy, deploytype, objfiles[filename], filename)
                 }
             }
         }
     });
     if (deploytype == "deploys") {
         $.ajax({type : 'GET', url: "/deploy/action/"+deploy, dataType : 'json',
             success: function (actions) {
                 expanded = "false" ; collapsed = " collapsed" ; toggle = "" ;
                 $('#'+id+'-accordion').append('<div id="panel-actions-'+id+'" class="panel panel-default'+collapsed+'">\
                 <div class="panel-heading" data-toggle="collapse" data-parent="#'+id+'-accordion" href="#collapse-actions-'+id+'" aria-expanded="'+expanded+'" style="cursor:pointer;">\
                   <h4 class="panel-title">\
                     <a data-toggle="collapse" data-parent="#'+id+'-accordion" href="#collapse-actions-'+id+'">Actions</a>\
                     </h4>\
                 </div>\
                 <div id="collapse-actions-'+id+'" class="panel-collapse collapse'+toggle+'">\
                 <div>\
                 <table style="font-weight: 300;width:100%;" id="'+id+'-table" class="table table-striped" cellspacing="0" width="100%">\
                 <thead>\
                     <tr style="cursor: pointer;">\
                     <td>Action</td>\
                     <td>Instances</td>\
                     <td>Tests</td>\
                     <td>Status</td>\
                     </tr>\
                 </thead>\
                 <tbody id="'+id+'-table-tbody"></tbody></table>\
                 </div>\
                 </div></div>');
                 for (i in actions) {
                         $('#'+id+'-table-tbody').append('\
                             <tr>\
                             <td>'+actions[i]["action"]+'</td>\
                             <td>'+actions[i]["clouds"]+'</td>\
                             <td>'+actions[i]["tests"]+'</td>\
                             <td>'+actions[i]["status"]+'</td>\
                             </tr>')
                 }
             }
         }); 
     }
 }
 function createfile(id, deploy, deploytype) {
     var filename = document.getElementById(id+'-inputfilename').value;
     appendfilecontent(id, deploy, deploytype, '', filename)
 }
 function savedeploy(id, deploy, deploytype) {
         $.ajax({
             url : '/deploy/save/'+deploytype+'/'+deploy,
             type: "POST",
             data : $('#'+id+'-form').serialize(),
             cache: false,
             processData:false,
             success: function (data) {
                 $('#'+id+'-form-button').addClass('btn-success').removeClass('btn-primary');
                 sleep(500).then(() => {
                 $('#'+id+'-form-button').addClass('btn-primary').removeClass('btn-success');
                 });
                 console.log('Deploy saved');
                 },
             error: function (data) {
                 $('#'+id+'-form-button').addClass('btn-danger').removeClass('btn-primary');
                 sleep(500).then(() => {
                 $('#'+id+'-form-button').addClass('btn-primary').removeClass('btn-danger');
                 });
                 console.log('An error occurred while saving deploy');
                 }
         })
 
 }
 function appendframe(id, deploy) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     sleep(250).then(() => {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/'+deploy+'/"></iframe>');
     });
 }
 function rundeploy(id, args) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cld-deploy/'+args+'"></iframe>');
     sleep(250).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
 }
 function openutil(id, util) {
     var args = document.getElementById(id+'-arg').value;
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/'+util+'/'+args+'"></iframe>');
     sleep(250).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
 }
 function deletedeploy(id, deploytype, deploy) {
     $.ajax({type : 'GET', url: '/deploy/delete/'+deploytype+'/'+deploy, dataType : 'text',
         success: function (data) {
             document.getElementById(id+'-li').remove();
             document.getElementById(id).remove();
             document.getElementById(deploytype+'-'+deploy).remove();
         }
     });
 }
 function newtab(deploy, deploytype) {
     var id = idgen();
     appendtab(id, deploy, deploytype);
     appendcontent(id, deploy, deploytype);
 };
 function newdeploytab(util) {
     var id = idgen();
     appenddeploytab(id, util);
     appenddeploycontent(id, util);
 };
 function appendform(id, util) {
     $('#'+id).append('<form onsubmit="openutil(\''+id+'\', \''+util+'\')">        <div class="form-group">          <label for="Arguments">Tool arguments:</label>          <input type="text" class="form-control" id="'+id+'-arg" placeholder="--arg1=value1 --arg2=value2 --debug">        </div>        <button type="button" class="btn btn-primary" onclick="openutil(\''+id+'\', \''+util+'\')" style="width: 10%;">Run</button>        </form>')
 }
 function appenddeploycontent(id, util) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     appendform(id, util);
     $.ajax({type : 'GET', url: "/help/"+util, dataType : 'text',
         success: function (data) {
         $('#'+id).append('<pre>'+data+'</pre>')
         }
     });
 }
 function newdirecttab(deploy) {
     var id = idgen();
     appendtab(id, deploy);
     appendframe(id, deploy);
 };
 function updatetab(id, deploy, deploytype) {
     $('#'+id).html('')
     appendcontent(id, deploy, deploytype);
 };
 function updatedeploytab(id, deploy, deploytype) {
     $('#'+id).html('')
     appenddeploycontent(id, deploy, deploytype);
 };

$(document).ready(function() {
 $('[data-toggle=offcanvas]').click(function() {
     $('.row-offcanvas').toggleClass('active');
 });
});