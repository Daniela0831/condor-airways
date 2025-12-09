document.addEventListener('DOMContentLoaded', function() {
    function tryInit() {
        const tipoField = document.getElementById('id_tipo');
        const codigoPreview = document.getElementById('id_codigo_preview');
        const codigoField = document.getElementById('id_codigo');
        const origenField = document.getElementById('id_origen');
        const destinoField = document.getElementById('id_destino');
        const fechaSalidaField = document.getElementById('id_fecha_salida');
        const horaSalidaField = document.getElementById('id_hora_salida');
        const fechaLlegadaField = document.getElementById('id_fecha_llegada');
        const horaLlegadaField = document.getElementById('id_hora_llegada');
        const tiempoVueloField = document.getElementById('id_tiempo_vuelo');
        const capacidadField = document.getElementById('id_capacidad');

        if (!tipoField) {
            setTimeout(tryInit, 100);
            return;
        }

        function setValues(value) {
            if (codigoPreview) codigoPreview.value = value;
            if (codigoField) codigoField.value = value;
        }

        // 🔹 Generar código automáticamente
        function updateCodigo() {
            const tipo = tipoField.value;
            if (!tipo) {
                setValues('Seleccione un tipo');
                return;
            }

            fetch(`/api/next-codigo/?tipo=${tipo}`, {method:"GET"})
                .then(response => response.json())
                .then(data => setValues(data.codigo))
                .catch(error => {
                    console.error('Error al obtener código:', error);
                    setValues('Error al generar código');
                });
        }

        // 🔹 Establecer capacidad automática según tipo
        function establecerCapacidadAutomatica() {
            const tipo = tipoField.value;
            if (!tipo || !capacidadField) return;

            capacidadField.value = tipo === 'NACIONAL' ? '150'
                              : tipo === 'INTERNACIONAL' ? '250'
                              : '';
        }

        // 🔹 Cargar opciones de origen/destino
        function updateOptions() {
            const tipo = tipoField.value;
            if (!tipo) {
                origenField.innerHTML = '<option value="">Seleccione el tipo de vuelo</option>';
                destinoField.innerHTML = '<option value="">Seleccione el tipo de vuelo</option>';
                return;
            }

            fetch(`/api/get_options/?tipo=${tipo}`, {method:"GET"})
                .then(response => response.json())
                .then(data => {
                    // Origen
                    origenField.innerHTML = '<option value="">Seleccione origen</option>';
                    data.origen_options.forEach(([val, text]) => {
                        const opt = document.createElement('option');
                        opt.value = val;
                        opt.textContent = text;
                        origenField.appendChild(opt);
                    });

                    // Destino
                    destinoField.innerHTML = '<option value="">Seleccione destino</option>';
                    data.destino_options.forEach(([val, text]) => {
                        const opt = document.createElement('option');
                        opt.value = val;
                        opt.textContent = text;
                        destinoField.appendChild(opt);
                    });
                })
                .catch(error => {
                    console.error('Error al obtener opciones:', error);
                    origenField.innerHTML = '<option value="">Error al cargar</option>';
                    destinoField.innerHTML = '<option value="">Error al cargar</option>';
                });
        }

        // 🔹 Calcular tiempo, fecha y hora de llegada
        function calcularTiempoVuelo() {
            const tipo = tipoField.value;
            const origen = origenField.value;
            const destino = destinoField.value;
            const fechaSalida = fechaSalidaField.value;
            const horaSalida = horaSalidaField.value;

            if (!tipo || !origen || !destino || !fechaSalida || !horaSalida) {
                if (tiempoVueloField) tiempoVueloField.value = '';
                if (fechaLlegadaField) fechaLlegadaField.value = '';
                if (horaLlegadaField) horaLlegadaField.value = '';
                return;
            }

            if (origen === destino) {
                alert('El origen y destino no pueden ser iguales.');
                return;
            }

            const params = new URLSearchParams({
                tipo, origen, destino, fecha_salida: fechaSalida, hora_salida: horaSalida
            });

            fetch(`/api/calcular_tiempo_vuelo/?${params}`, {method:"GET"})
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(`Error al calcular tiempo de vuelo: ${data.error}`);
                        return;
                    }

                    if (tiempoVueloField) tiempoVueloField.value = data.tiempo_vuelo;
                    if (fechaLlegadaField) fechaLlegadaField.value = data.fecha_llegada;
                    if (horaLlegadaField) horaLlegadaField.value = data.hora_llegada;
                })
                .catch(error => console.error('Error al calcular tiempo de vuelo:', error));
        }

        // 🔹 Event Listeners
        tipoField.addEventListener('change', () => {
            updateCodigo();
            updateOptions();
            establecerCapacidadAutomatica();
            calcularTiempoVuelo();
        });

        if (origenField) origenField.addEventListener('change', calcularTiempoVuelo);
        if (destinoField) destinoField.addEventListener('change', calcularTiempoVuelo);
        if (fechaSalidaField) fechaSalidaField.addEventListener('change', calcularTiempoVuelo);
        if (horaSalidaField) horaSalidaField.addEventListener('change', calcularTiempoVuelo);

        // Inicializar al cargar
        updateCodigo();
        updateOptions();
        establecerCapacidadAutomatica();
    }

    tryInit();
});
