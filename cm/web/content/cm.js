 function appendtab(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper) {
     $('#hostTab').append('<li class="nav-item" id="' + id + '-li"><a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false"><button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button><button class="refreshtab" type="button" onclick="updatetab(\''+id+'\', \''+name+'\', \''+kvmid+'\', \''+status+'\', \''+cpu+'\', \''+ram+'\', \''+disk+'\', \''+whiteips+'\', \''+grayips+'\', \''+hyper+'\')">⟳</button>' + name + '</a></li>'
     );
 }
 function appendhprtab(id, name) {
     $('#hostTab').append('<li class="nav-item" id="' + id + '-li"><a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false"><button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button><button class="refreshtab" type="button" onclick="updatehprtab(\''+id+'\', \''+name+'\')">⟳</button>' + name + '</a></li>'
     );
 }
 function appendform(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper) {
     $('#'+id).append('\
         <div style="font-family: monospace;font-weight: bold;font-variant-caps: petite-caps;font-size: larger;">\
         <div>name: <div class="prein">' + name.toUpperCase() + '</div></div>\
         <div>id: <div class="prein">' + kvmid.toUpperCase() + '</div></div>\
         <div>status: <div class="prein">' + status.toUpperCase() + '</div></div>\
         <div>cpu: <div class="prein">' + cpu.toUpperCase() + '</div></div>\
         <div>ram: <div class="prein">' + ram.toUpperCase() + '</div></div>\
         <div>disk: <div class="prein">' + disk.toUpperCase() + '</div></div>\
         <div>white ip: <div class="prein">' + whiteips.toUpperCase() + '</div></div>\
         <div>private ip: <div class="prein">' + grayips.toUpperCase() + '</div></div>\
         </div>\
         <button type="button" class="btn btn-success" onclick="controlkvm(\''+id+'\', \''+kvmid+'\', \'start\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Start KVM</button>\
         <button type="button" class="btn btn-danger" onclick="controlkvm(\''+id+'\', \''+kvmid+'\', \'stop\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Stop KVM</button>\
         <button type="button" class="btn btn-danger" onclick="controlkvm(\''+id+'\', \''+kvmid+'\', \'reset\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Reset KVM</button>\
         <button type="button" class="btn btn-success" onclick="controlkvm(\''+id+'\', \''+kvmid+'\', \'resume\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Resume KVM</button>\
         <button type="button" class="btn btn-warning" onclick="controlkvm(\''+id+'\', \''+kvmid+'\', \'suspend\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Suspend KVM</button><br>\
         <button type="button" class="btn btn-info" onclick="startmigrate(\''+id+'\', \''+kvmid+'\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Migrate KVM</button><br>\
         <button type="button" class="btn btn-primary" onclick="cmterminal(\''+id+'\', \''+kvmid+'\', \''+hyper+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">KVM Terminal</button><br><br>\
         <button type="button" class="btn btn-dark" onclick="destroykvm(\''+id+'\', \''+hyper+'\', \''+kvmid+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Destroy KVM</button>\
         ')
 }
 function appendcontent(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     appendform(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper);
     // $.ajax({type : 'GET', url: "/help/"+util, dataType : 'text',
     //     success: function (data) {
     //     $('#'+id).append('<pre>'+data+'</pre>')
     //     }
     // });
 }
 function appendhprcontent(id, name) {
     $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
     document.getElementById(id + "-tab").click();
     $.ajax({type : 'GET', url: "/webapi/tool/cld-cm/--json --minify --hypers="+name, dataType : 'text',
         success: function (data) {
         var obj = JSON.parse(data);
         $('#'+id).append('\
          <div style="font-family: monospace;font-weight: bold;font-variant-caps: petite-caps;font-size: larger;">\
          <div>cores: <div class="prein">' + obj[0].resources.cores + '</div></div>\
          <div>free cores: <div class="prein">' + obj[0].resources.free_cores + '</div></div>\
          <div>ram: <div class="prein">' + obj[0].resources.ram + '</div></div>\
          <div>free ram: <div class="prein">' + obj[0].resources.free_ram + '</div></div> </div>')
         for (i in obj[0].storages) {
             var storage = obj[0].storages[i];
             $('#'+id).append('<br>\
             <div style="font-family: monospace;font-weight: bold;font-variant-caps: petite-caps;font-size: larger;">\
             <div>storage name: <div class="prein">' + storage.name + '</div></div>\
             <div>size: <div class="prein">' + storage.size + '</div></div>\
             <div>allocated: <div class="prein">' + storage.allocated + '</div></div>\
             <div>free: <div class="prein">' + storage.free + '</div></div>\
             <div>fragmentation: <div class="prein">' + storage.fragmentation + '</div></div>\
             <div>capacity: <div class="prein">' + storage.capacity + '</div></div>\
             <div>health: <div class="prein">' + storage.health + '</div></div>\
             </div>\
             ')
         }
         $('#'+id).append('\
         <button type="button" class="btn btn-success" onclick="createkvm(\''+id+'\', \''+name+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Create KVM</button>\
         <button type="button" class="btn btn-primary" onclick="cldx(\''+id+'\', \''+name+'\')" style="width: 10%;min-width: 120px;margin-top: 10px;">Terminal</button>\
         ')
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
 function startmigrate(id, kvmid, hyper) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cld-cmmigrate/--id='+kvmid+' --source='+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function cmterminal(id, kvmid, hyper) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cld-cmterm/--id='+kvmid+' --hyper='+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function createkvm(id, hyper) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cld-cmcreate/--hyper='+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function cldx(id, hyper) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cldx/'+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function destroykvm(id, hyper, kvmid) {
     $('#'+id).html('<p>To confirm the operation please type it manually in the terminal:<p>\
 <pre><p>qm stop '+kvmid+'</p>\
 <p>qm destroy '+kvmid+'</p></pre>\
     <iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cldx/'+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function controlkvm(id, kvmid, cmd, hyper) {
     $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/cld-cmcontrol/--id='+kvmid+' --cmd='+cmd+' --hyper='+hyper+'"></iframe>');
     sleep(2000).then(() => {
     console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
     document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
     });
     };
 function newhprtab(name) {
     var id = idgen();
     appendhprtab(id, name);
     appendhprcontent(id, name);
 };
 function newtab(name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper) {
     var id = idgen();
     appendtab(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper);
     appendcontent(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper);
 };
 function newdirecttab(util) {
     var id = idgen();
     appendtab(id, util);
     appendframe(id, util);
 };
 function updatetab(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper) {
     $('#'+id).html('')
     appendcontent(id, name, kvmid, status, cpu, ram, disk, whiteips, grayips, hyper);
 };
 function updatehprtab(id, name) {
     $('#'+id).html('')
     appendhprcontent(id, name);
 };
 
 $(document).ready(function() {
     $('[data-toggle=offcanvas]').click(function() {
         $('.row-offcanvas').toggleClass('active');
     });
 });