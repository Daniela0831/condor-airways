document.addEventListener('DOMContentLoaded', () => {

    /* CONFIGURACIÓN AVIÓN INTERNACIONAL (≈250) */
    const BUSINESS_ROWS = 6;
    const ECON_ROWS = 38;
    const ECON_START = 7;

    const SEAT_W = 38;
    const SEAT_H = 28;
    const LEFT_X = 290;
    const RIGHT_X = 640;
    const GAP_X = 70;
    const TOP_Y = 320;
    const ROW_GAP = 58;
    const CENTER_X = 550;

    const emergencyRows = [14, 15];
    const ocupados = window.ocupados || [];
    const seatsLayer = document.getElementById('seats-layer');

    function svg(tag, attrs = {}) {
        const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (let k in attrs) el.setAttribute(k, attrs[k]);
        return el;
    }

    function createSeat(x, y, seatId, state) {
        const g = svg('g', { class: 'seat' });

        const rect = svg('rect', {
            x,
            y,
            width: SEAT_W,
            height: SEAT_H,
            rx: 6,
            ry: 6,
            class: state
        });

        rect.setAttribute('title', seatId);

        const text = svg('text', {
            x: x + SEAT_W / 2,
            y: y + SEAT_H / 2 + 4,
            'text-anchor': 'middle',
            class: 'seat-label'
        });
        text.textContent = seatId;

        g.append(rect, text);

        if (!rect.classList.contains('seat-occupied')) {
            g.addEventListener('click', () => selectSeat(rect, seatId));
        }
        return g;
    }

    function selectSeat(rect, id) {
      // Primero, deseleccionamos cualquier asiento que esté seleccionado
      document.querySelectorAll('rect.seat-selected').forEach(r => {
          r.classList.remove('seat-selected');
          
          // Restaurar la clase original según si era business o economy
          if (r.dataset.seatClass) {
              r.classList.add(r.dataset.seatClass);
          } else {
              r.classList.add('seat-free'); // fallback
          }
      });

      // Si el asiento está ocupado, no hacemos nada
      if (rect.classList.contains('seat-occupied')) return;

      // Guardamos la clase original en un atributo data para poder restaurarla
      if (!rect.dataset.seatClass) {
          if (rect.classList.contains('seat-business')) rect.dataset.seatClass = 'seat-business';
          else if (rect.classList.contains('seat-economy')) rect.dataset.seatClass = 'seat-economy';
          else rect.dataset.seatClass = 'seat-free';
      }

      // Seleccionamos el nuevo asiento
      rect.classList.remove('seat-business', 'seat-economy', 'seat-free');
      rect.classList.add('seat-selected');

      // Guardamos el valor en el input oculto
      document.getElementById('seat-selected').value = id;
    }

    function render() {
        let index = 0;
        const rows = [];

        for (let i = 1; i <= BUSINESS_ROWS; i++) rows.push(i);
        for (let i = 0; i < ECON_ROWS; i++) rows.push(ECON_START + i);

        rows.forEach(row => {
            const y = TOP_Y + index * ROW_GAP;

            ['A','B','C','D','E','F'].forEach((l, i) => {
                const x = i < 3
                    ? LEFT_X + i * GAP_X
                    : RIGHT_X + (i - 3) * GAP_X;

                const id = `${row}${l}`;

                let state;
                if (ocupados.includes(id) || emergencyRows.includes(row)) {
                    state = 'seat-occupied';
                } else if (row <= BUSINESS_ROWS) {
                    state = 'seat-business';
                } else {
                    state = 'seat-economy';
                }

                seatsLayer.appendChild(createSeat(x, y, id, state));
            });

            const rowText = svg('text', {
                x: CENTER_X,
                y: y + SEAT_H / 2 + 4,
                'text-anchor': 'middle',
                class: 'row-number'
            });
            rowText.textContent = row;
            seatsLayer.appendChild(rowText);

            index++;
        });
    }

    render();

    document.getElementById('confirm').onclick = () => {
        if (!document.getElementById('seat-selected').value) {
            alert('Selecciona un asiento');
            return;
        }
        document.getElementById('hidden-pasajero').value =
            document.getElementById('pasajero_id').value;
        document.getElementById('seat-form').submit();
    };

    document.getElementById('clear').onclick = () => {
        document.querySelectorAll('.seat-selected')
            .forEach(r => r.classList.remove('seat-selected'));

        document.getElementById('seat-selected').value = '';
    };
});
