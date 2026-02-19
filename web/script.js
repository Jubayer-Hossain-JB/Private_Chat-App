let display = document.getElementById('display');
let msg_box = document.getElementById('msg');
let attach = document.getElementById('attach');
let send_btn = document.getElementById("send");
let send_box = document.getElementById('send_box');
let active_users = document.getElementById('active_users')

let addss = window.location.hostname
let socket= new WebSocket('ws://'+addss+':5005');


let user_name;
let user_id;
let cook = document.cookie.split('; ')
/* User Account*/
cook.forEach(a=>{
    c = a.split('=') 
    if(c[0]=='usr_name'){
        user_name = c[1]
        return
    }else if(c[0]=='usr_id'){
        user_id = c[1]
        return
    }
})
/* ******************* */

socket.onopen= function() {
    socket.send(JSON.stringify({
        'type': 'configure',
        'userId': user_id,
        'userName': user_name
    }));
};
socket.onmessage= function(s) {
    let data = JSON.parse(s.data)
    switch(data.type){
        case "chat_history":
            let chat_history = JSON.parse(data.data)
            for(var i=0; i<chat_history.length; i++){
                display_msg(chat_history[i])
            }
            break;
        case "active_users":
            for(u of data.data){
                active_users.innerHTML += '<div class="user_entry">'+u+'</div>'
            }
            break;
        case "add_active_user":
            var usr = document.createElement('div')
            usr.innerHTML = data.data
            usr.classList.add('user_entry')
            active_users.appendChild(usr)
            break;
        case "remove_active_user":
            active_users.children.item(data.data).classList.add('user_closed')
            setTimeout(()=>{active_users.removeChild(active_users.children.item(data.data))}, 500)
            break;
        default:
            display_msg(data)   
    }
};
function send(e){
    text = msg_box.value.replace('\n', '</br>')    
    if(attach.files.length == 1){
        msg_box.classList.remove('hidden');
        attach.classList.remove('hidden');
        switch(f_ext){
            case 'jpg':
            case 'png':
            case 'jpeg':
                my_img = document.createElement('img');
                my_img.classList.add('my_image');
                my_img.classList.add('my_msg');
                my_img.src = URL.createObjectURL(attach.files[0]);
                display.appendChild(my_img);
                break;
            default:
                block = document.createElement('div');
                block.classList.add('show_file');   
                block.classList.add('my_msg');            
                block.innerHTML = '1 '+f_ext+' File Sent';
                display.appendChild(block);
            }
            var data = new FormData()
            data.append('file', attach.files[0])
            // data.append('user', 'hubot')
                
            file_upload(data).then(e=>JSON.parse(e)).then(d=>{
            data = JSON.stringify({
                'sender': user_id,
                'type': 'singleFile',
                'data' :d
            })
            socket.send(data)
        })
    

        attach.value = null;
        file.removeChild(document.getElementById('f_content'))
        send_box.removeChild(file);
    }
    else if(attach.files.length>1){
        msg_box.classList.remove('hidden');
        attach.classList.remove('hidden');
        block = document.createElement('div');
        block.classList.add('show_file');   
        block.classList.add('my_msg');            
        block.innerHTML = attach.files.length+' File Sent';
        display.appendChild(block);
        var data = new FormData()
        for(var x=0; x < attach.files.length; x++){
            data.append('file'+x, attach.files[x])
        }
        // data.append('user', 'hubot')
        
        file_upload(data).then(e=>JSON.parse(e)).then(d=>{
            
            data = JSON.stringify({
                'sender': user_id,
                'type': 'multiFile',
                'data' :d
            })
    
            socket.send(data)
        })
        
        attach.value = null;
        file.removeChild(document.getElementById('f_content'))
        send_box.removeChild(file);
    }
    else if (text){
        msg_box.value = "";
        p = document.createElement('p');
        p.classList.add('my_msg');
        p.innerHTML = text;
        display.appendChild(p);
        data = JSON.stringify({
            'sender': user_id,
            'type': 'text',
            'data' :text
        })
        socket.send(data)  
    }
    display.scrollTo(0, display.getBoundingClientRect().height)
}
const prog = document.querySelector('.prog')
function file_upload(data){
    const xhr = new XMLHttpRequest();
    let time;
    xhr.open('POST', '/file_upload', true);
    xhr.upload.addEventListener("loadstart", (event) => {
        time = setTimeout(()=>{
            prog.style.display='block'
        },200)
    });
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        prog.innerHTML = Math.round(percentComplete)+'%'
        if(percentComplete==100){
            clearTimeout(time)
            setTimeout(()=>{
                prog.style.display='none',
                500
            })
        }
        // Update UI (progress bar, remaining time display, etc.)
        // document.getElementById('progressBar').style.width = percentComplete + '%';
      }
    });
    let promise = new Promise((resolve, reject) =>{
        xhr.onload = () => {
        if (xhr.status === 200) {
            resolve(xhr.response);
        } else {
          reject("Unable to upload");
        }
      };
    });
    
    xhr.send(data);
    return promise;
}
function display_msg(data){
    let wraper = document.createElement('div')
    if (data.sender==user_id){
        wraper.classList.add('my_msg')
    }else{
        wraper.classList.add('incoming_message')
        var sender = document.createElement('p')
        sender.classList.add('sender')
        sender.innerHTML = data.sender;
        wraper.appendChild(sender)
    }
    switch(data.type){
        case "text":
            var msg = document.createElement('p')
            msg.classList.add('msg_body')
            msg.innerHTML = data.data
            wraper.appendChild(msg)
            break;
        default:
            for(var i=0; i<data.data.length;i++){
                var msg = document.createElement('a');
                msg.classList.add('msg_file');
                f_name = data.data[i].split('.')
                f_ext = f_name[f_name.length-1].toLowerCase();
                var params = new URLSearchParams({
                    file : data.data[i]
                });
                msg.setAttribute('href',"./get?"+params.toString())
                switch(f_ext){
                    case 'jpg':
                    case 'png':
                    case 'jpeg':
                        my_img = document.createElement('img');
                        my_img.classList.add('sent_image');
                        my_img.src = "./get?"+params.toString()
                        msg.appendChild(my_img)
                        break;
                    case 'doc':
                    case 'docx':
                        msg.innerHTML = "Word File Attached";
                        break;
                    default:
                        msg.innerHTML = f_ext.toUpperCase()+" File Attached";                    
                }
                wraper.appendChild(msg)
            }
    }
    display.appendChild(wraper)
    display.scrollTo(0, display.getBoundingClientRect().height)
}

send_btn.addEventListener('click', send);
msg_box.focus();
// msg_box.addEventListener('keypress', e=>{
//     if(e.key === 'Enter') send(e);
    
// })


var file;
var f_ext;
var cls = document.createElement('div');
cls.id = 'file_close'
cls.innerHTML = "×"
cls.addEventListener('click', ()=>{
    msg_box.classList.remove('hidden');
    attach.classList.remove('hidden');
    file.removeChild(document.getElementById('f_content'))
    send_box.removeChild(file);
    attach.value = null;
})
file = document.createElement('div');
file.classList.add('file');
file.appendChild(cls)
attach.addEventListener('change',()=>{
    if(attach.files.length<2){
        f_name = attach.files[0].name.split('.')
        f_ext = f_name[f_name.length-1].toLowerCase();
        switch(f_ext){
            case 'jpg':
            case 'png':
            case 'jpeg':
                img = document.createElement('img');
                img.classList.add('my_image');
                img.id = 'f_content'
                img.src = URL.createObjectURL(attach.files[0]);
                file.appendChild(img)
                send_box.insertBefore(file, send_btn);
                msg_box.classList.add('hidden');
                attach.classList.add('hidden');
                break;
            default:
                block = document.createElement('div');
                block.classList.add('show_file');                
                block.innerHTML = '1 File selected';
                block.id = 'f_content'
                file.appendChild(block)
                send_box.insertBefore(file, send_btn);
                msg_box.classList.add('hidden');
                attach.classList.add('hidden');
        }
    }else{
        block = document.createElement('div');
        block.classList.add('show_file');                
        block.innerHTML = attach.files.length+' File selected';
        block.id = 'f_content'
        file.appendChild(block)
        send_box.insertBefore(file, send_btn);
        msg_box.classList.add('hidden');
        attach.classList.add('hidden');
    }
    
})
