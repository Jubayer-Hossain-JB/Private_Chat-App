from datetime import datetime
import socket
import json
import websocket_server

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
class Messager_Server:
    def __init__(self, shared_dict):
        self.client_list = []
        self.uids_users = dict()
        self.uids = []
        self.active_uids = []
        self.chat_history = []
        self.shared_dict = shared_dict
# def handle_new_client(client, server):
#     print(f"New client connected: {client['address']}")
#     server.send_message(client, "Hello, client!")
#     client_list.append(client)
    def update_vars(self):
        self.uids = self.shared_dict.get('uids')
        self.uids_users = self.shared_dict.get('uids_users')

    def handle_client_left(self, client, server):
        if client in self.client_list:
            print(f"Client {client['address']} left")
            msg = json.dumps({
                'type':'remove_active_user',
                'data': self.client_list.index(client)
            })
            for c in self.client_list:
                if c != client:
                    server.send_message(c, msg)
            del self.active_uids[self.client_list.index(client)]
            self.client_list.remove(client)
    def handle_client_message(self, client, server, message):
        data = json.loads(message)
        self.update_vars()
        try:
            ## Configuring a new commer
            if data['type'] == 'configure':
                if data['userId'] in self.uids:
                    self.client_list.append(client)
                    self.active_uids.append(data['userId'])
                    ## The block sends a string of chat hsitory
                    chats = json.dumps(self.chat_history[-10:])
                    for uid in self.uids:
                        if uid==data['userId'] :
                            continue
                        else:
                            chats = chats.replace(uid, self.uids_users[uid])
                    msg = {
                        'type':'chat_history',
                        'data': chats,
                    }
                    server.send_message(client, json.dumps(msg))
                    ####
                    ## The block sends a string of active users
                    a_users = []
                    for a in self.active_uids:
                        a_users.append(self.uids_users[a])
                    msg = json.dumps({
                        'type':'active_users',
                        'data': a_users,
                    })
                    server.send_message(client, msg)
                    ###
                    ## The block broadcasts to other client about the new commer
                    msg = json.dumps({
                        'type':'add_active_user',
                        'data': self.uids_users[data['userId']],
                    })
                    for c in self.client_list:
                        if c != client:
                            server.send_message(c, msg)
            ## Below block is to handle messages
            elif data['type'] == 'text' or data['type'] == 'multiFile' or data['type'] == 'singleFile':
                sender = data['sender']
                msg = {
                    'timestamp': str(datetime.today()),
                    'sender' : self.uids_users[data['sender']],
                    'type': data['type'],
                    'data' :data['data']
                }
                for c in self.client_list:
                    if c != client:
                        server.send_message(c, json.dumps(msg))
                msg['sender']=sender
                self.chat_history.append(msg)
            ## NO entry to the faceless
            else:
                server.send_close(reason="Unauthorized")
        except:
            pass

    def run_server(self):
        server = websocket_server.WebsocketServer(host=IPAddr,port=5005)
        # server.set_fn_new_client(handle_new_client)
        server.set_fn_message_received(self.handle_client_message)
        server.set_fn_client_left(self.handle_client_left)
        server.run_forever()
