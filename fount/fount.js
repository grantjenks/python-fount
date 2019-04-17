Fount = {
    convert: function (value) {
        if (typeof value === 'string' || value instanceof String) {
            return value;
        }
        else if (value instanceof Array) {
            return value.map(Fount.convert);
        }
        if (value['tag'] == 'button' && value['props']['type'] == 'button') {
            value['props']['onClick'] = clicker;
        }
        return React.createElement(
            value['tag'],
            value['props'],
            Fount.convert(value['children'])
        );
    },
    connect: function (element, url) {
        var socket = new WebSocket(url);
        socket.onmessage = function (event) {
            var message = JSON.parse(event.data);
            var react_element = Fount.convert(message);
            ReactDOM.render(react_element, element);
        };
    }
}
