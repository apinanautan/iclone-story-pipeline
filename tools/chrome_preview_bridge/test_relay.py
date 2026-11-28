import relay,threading,urllib.request,urllib.error
server=relay.ThreadingHTTPServer(('127.0.0.1',0),relay.Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}'
try:
    req=urllib.request.Request(url+'/preview',headers={'X-Preview-Key':relay.KEY})
    with urllib.request.urlopen(req) as r:
        data=r.read();assert data==relay.IMAGE.read_bytes()
        print('PASS actual iClone preview bytes',len(data))
    for path,key in [('/preview','bad'),('/anything',relay.KEY)]:
        try:urllib.request.urlopen(urllib.request.Request(url+path,headers={'X-Preview-Key':key}));raise AssertionError('unexpected access')
        except urllib.error.HTTPError as e:assert e.code==403
    print('PASS wrong key and other paths rejected')
finally:server.shutdown();server.server_close()
