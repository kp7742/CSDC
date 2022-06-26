$(function() {
  let INDEX = 0;
  let isGreeted = false;

  const socket = io("http://localhost:8282");
  socket.on('connect', () => {});
  socket.on('disconnect', () => {socket.open();});

  $("#chat-submit").click(function(e) {
    e.preventDefault();
    const msg = $("#chat-input").val();
    if(msg.trim() === ''){
      return false;
    }
    generate_message(msg, 'self');
    socket.emit("chatbot", {"Answer": msg}, (data) => {
        for(let i=0; i < data.len; i++){
              let msg = data.msgs[i];
              if(msg.hasbuttons){
                    generate_button_message(msg.question, msg.buttons);
              } else if(data.question !== "[NIL]"){
                    generate_message(msg.question, 'user');
              }
        }
    });
  });

  function generate_message(msg, type) {
    INDEX++;
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg "+type+"\">";
    str += "          <div class=\"cm-msg-text\">";
    str += msg;
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);
    if(type == 'self'){
		$("#chat-input").val(''); 
    }    
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);
  }  
  
  function generate_button_message(msg, buttons){
    /* Buttons should be object array 
      [
        {
          name: 'Existing User',
          value: 'existing'
        },
        {
          name: 'New User',
          value: 'new'
        }
      ]
    */
    INDEX++;
    var btn_obj = buttons.map(function(button) {
       return "              <li style=\"width: auto\"><div class=\"cm-msg-text\" style=\"background:transparent;padding: 4px 8px\"><a href=\"javascript:;\" class=\"btn btn-primary chat-btn\" chat-value=\""+button.value+"\">" + button.name + "<\/a><\/div><\/li>";
    }).join('');
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg user\">";
    str += "          <div class=\"cm-msg-text\" style=\"margin-bottom: 10px\">";
    str += msg;
    str += "          <\/div>";
    str += "          <div class=\"cm-msg-button\">";
    str += "            <ul>";   
    str += btn_obj;
    str += "            <\/ul>";
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);   
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);
    $("#chat-input").attr("disabled", true);
  }
  
  $(document).delegate(".chat-btn", "click", function() {
    var value = $(this).attr("chat-value");
    var name = $(this).html();
    $("#chat-input").attr("disabled", false);
    generate_message(name, 'self');
    socket.emit("chatbot", {"Answer": value}, (data) => {
        for(let i=0; i < data.len; i++){
              let msg = data.msgs[i];
              if(msg.hasbuttons){
                    generate_button_message(msg.question, msg.buttons);
              } else if(data.question !== "[NIL]"){
                    generate_message(msg.question, 'user');
              }
        }
    });
  });
  
  $("#chat-circle").click(function() {
    if(!isGreeted){
      socket.emit("greetings", {}, (data) => {
          for(let i=0; i < data.len; i++){
              let msg = data.msgs[i];
              setTimeout(() => {
                generate_message(msg.msg, 'user');
              }, msg.delay);
          }
      });
      isGreeted = true;
    }
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  });
  
  $(".chat-box-toggle").click(function() {
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  });

  function addLiveCircle() {
    document.getElementById('titleid').textContent += "🟢";
  }

  function removeLiveCircle() {
    document.getElementById('titleid').textContent = "Corona ChatBot";
  }
});