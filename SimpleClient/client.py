
from jsonrpclib import Server
server = Server('http://127.0.0.1:8080/rpc')
print server.add(2, 6)

exit()
result = server.tree.power(2, 6)

print result

print server.echo("echome")
