var socket = io.connect('http://127.0.0.1:2137');
socket.on('connect',function(){
socket.send('START');
});
socket.on('message',function(msg){
console.log('received');
});