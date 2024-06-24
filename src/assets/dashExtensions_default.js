window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            return L.marker(latlng, {
                icon: L.AwesomeMarkers.icon({
                    icon: 'fire',
                    prefix: 'fa',
                    markerColor: 'red'
                })
            });
        },
        function1: function(feature, latlng) {
            return L.marker(latlng, {
                icon: L.AwesomeMarkers.icon({
                    icon: 'fire',
                    prefix: 'fa',
                    markerColor: 'green'
                })
            });
        }
    }
});