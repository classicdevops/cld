function escapeHtml(unsafe) {
return unsafe
   .replace(/&/g, "&amp;")
   .replace(/</g, "&lt;")
   .replace(/>/g, "&gt;")
   .replace(/"/g, "&quot;")
   .replace(/'/g, "&#039;");
}
function appendtab(id, note) {
  $('#hostTab').append('<li class="nav-item" id="' + id + '-li">\
      <a class="nav-link" id="' + id + '-tab" data-toggle="tab" href="#' + id + '" role="tab" aria-controls="' + id + '" aria-selected="false">\
      <button class="closetab" type="button" onclick="document.getElementById(\'' + id + '-li\').remove();document.getElementById(\'' + id + '\').remove();">×</button>\
      <button class="refreshtab" type="button" onclick="updatetab(\''+id+'\', \''+note+'\')">⟳</button>' + note + '\
      </a></li>'
  );
}
function appendfilecontent(id, note, filecontent, filenamestr) {
  var filename = filenamestr.replace(' ', '_')
  expanded = "true" ; collapsed = "" ; toggle = " in" ;
  $('#'+id+'-accordion').append(`<div id="panel`+filename+id+`" class="panel panel-default`+collapsed+`">
      <div class="panel-heading" data-toggle="collapse" data-parent="#`+id+`-accordion" href="#collapse`+id+filename+`" aria-expanded="`+expanded+`" style="cursor:pointer;">
        <h4 class="panel-title">
          <a data-toggle="collapse" data-parent="#`+id+`-accordion" href="#collapse`+id+filename+`">
                  file: `+filenamestr+`</a>
          </h4>
          <button class="btn btn-danger dpl_del_file_btn" onclick="deletenotefile('`+id+`', '`+note+`', '`+filenamestr+`')">✖</button>
          <div style="float: right;margin: -17px 15px -20px 0px;">
          <input id="link`+id+filename+`" class="prelink" value='bash -x <(wget -qO- "https://`+cld_domain+`/api/all/note/`+note+`/`+filenamestr+`?hash=`+CryptoJS.MD5(note+filenamestr+userapitoken).toString()+`")' readonly></div>
      </div>
      <div id="collapse`+id+filename+`" class="panel-collapse collapse`+toggle+`">
          <div class="panel-body aceinit">
      <pre id="`+filename+id+`">`+escapeHtml(filecontent)+`</pre>
      </div></div></div>`);
  $('#link'+id+filename)[0].style.width = (($('#link'+id+filename)[0].value.length) * 5.62) + 'px';
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
function deletenotefile(id, note, filename) {
  $.ajax({type : 'GET', url: '/note/delete/'+note+'/'+filename, dataType : 'text',
      success: function (data) {
          document.getElementById("panel"+filename.replace(' ', '_')+id).remove();
          document.getElementById("textarea"+filename.replace(' ', '_')+id).remove();
      }
  });
}
function appendcontent(id, note) {
  String.prototype.capitalize = function() {
      return this.charAt(0).toUpperCase() + this.slice(1);
  }
  $('#hostTabContent').append('<div class="tab-pane fade" id="' + id + '" role="tabpanel" aria-labelledby="' + id + '-tab"></div>');
  document.getElementById(id + "-tab").click();
  $('#'+id).append('<div class="panel-group" id="'+id+'-accordion"></div>')
  $('#'+id+'-accordion').append('Note: '+note+'<br><br>')
  $('#'+id+'-accordion').append('\
      <button type="button" class="btn btn-primary" onclick="savenote(\''+id+'\', \''+note+'\')" id="'+id+'-form-button" style="width: 10%; min-width: 120px;">Save note</button>  \
      <button type="button" class="btn btn-danger" onclick="deletenote(\''+id+'\', \''+note+'\')" style="width: 10%; min-width: 120px;">Delete note</button>\
      <form style="display: -webkit-inline-box;margin-left: 5;" onsubmit="createfile(\''+id+'\', \''+note+'\');return false;">\
      <input type="text" class="form-control" id="'+id+'-inputfilename" placeholder="New file name" style="width: 45%;padding-top: 3;">\
      <button type="submit" class="btn btn-primary" style="margin-left: -5; border-radius: 0px 4px 4px 0px;">Create</button></form>\
      <br><br>')
  $('#'+id+'-accordion').append('<form id="'+id+'-form" style="display: none;"></form>')
  $.ajax({type : 'GET', url: "/note/"+note+"/files", dataType : 'json',
      success: function (objfiles) {
          for (filename in objfiles) {
              if (filename != ""){
                  appendfilecontent(id, note, objfiles[filename], filename)
              }
          }
      },
      error: function (objfiles) {
          appendfilecontent(id, note, '', "script")
      }
  });
}
function createfile(id, note) {
  var filename = document.getElementById(id+'-inputfilename').value.replaceAll(' ', '_');
  if (filename == "") { var filename = "script" };
  appendfilecontent(id, note, '', filename)
}
function savenote(id, note) {
      $.ajax({
          url : '/note/save/'+note,
          type: "POST",
          data : $('#'+id+'-form').serialize(),
          cache: false,
          processData:false,
          success: function (data) {
              $('#'+id+'-form-button').addClass('btn-success').removeClass('btn-primary');
              sleep(500).then(() => {
              $('#'+id+'-form-button').addClass('btn-primary').removeClass('btn-success');
              });
              console.log('Note saved');
              },
          error: function (data) {
              $('#'+id+'-form-button').addClass('btn-danger').removeClass('btn-primary');
              sleep(500).then(() => {
              $('#'+id+'-form-button').addClass('btn-primary').removeClass('btn-danger');
              });
              console.log('An error occurred while saving note');
              }
      })

}
function openutil(id, util) {
  var args = document.getElementById(id+'-arg').value;
  $('#'+id).html('<iframe id="frame-' + id + '" width="800" height="800" style="visibility:visible;height: 70%; width: 100%; resize: both; border: 0px;" src="/tool/'+util+'/'+args+'"></iframe>');
  sleep(250).then(() => {
  console.log("document.getElementById('frame-"+id+"').contentWindow.document.getElementsByClassName('xterm-cursor-layer')[0].click();")
  document.getElementById('frame-' + id).contentDocument.querySelector('.xterm-helper-textarea').focus();
  });
}
function deletenote(id, note) {
  $.ajax({type : 'GET', url: '/note/delete/'+note, dataType : 'text',
      success: function (data) {
          document.getElementById(id+'-li').remove();
          document.getElementById(id).remove();
          document.getElementById(note).remove();
      }
  });
}
function newtab(note) {
  var id = idgen();
  appendtab(id, note);
  appendcontent(id, note);
};
function updatetab(id, note) {
  $('#'+id).html('')
  appendcontent(id, note);
};

function search() {
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById("searchInput");
  filter = input.value.toUpperCase();
  ul = document.getElementById("ServerListUl");
  li = ul.getElementsByTagName("li");
  for (i = 0; i < li.length; i++) {
      a = li[i].getElementsByTagName("a")[0] || li[i].getElementsByTagName("span")[0];
      txtValue = a.textContent || a.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
          li[i].style.display = "";
      } else {
          li[i].style.display = "none";
      }
  }
}

$(document).ready(function() {
  $('[data-toggle=offcanvas]').click(function() {
      $('.row-offcanvas').toggleClass('active');
  });
});
