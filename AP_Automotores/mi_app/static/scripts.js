/* ═══════════════════════════════════════════════════════════════════
   scripts.js — Lógica de la app mi_app
   ═══════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  /* ══════════════════════════════════════════════════════════
     1. TABS DEL FORMULARIO
  ══════════════════════════════════════════════════════════ */
  var tabs     = document.querySelectorAll('.tab');
  var contents = document.querySelectorAll('.tab-content');

  function activarTab(id) {
    tabs.forEach(function (t) {
      t.classList.toggle('tab--active', t.dataset.tab === id);
    });
    contents.forEach(function (c) {
      c.classList.toggle('tab-content--active', c.id === 'tab-' + id);
    });
  }

  tabs.forEach(function (t) {
    t.addEventListener('click', function () { activarTab(t.dataset.tab); });
  });
  document.querySelectorAll('.tab-next').forEach(function (btn) {
    btn.addEventListener('click', function () { activarTab(btn.dataset.next); });
  });
  document.querySelectorAll('.tab-prev').forEach(function (btn) {
    btn.addEventListener('click', function () { activarTab(btn.dataset.prev); });
  });

  // Si Django devolvió errores → abrir el tab donde está el primer error
  var erroresData = document.getElementById('form-errors-data');
  if (erroresData) {
    try {
      var errKeys       = Object.keys(JSON.parse(erroresData.textContent));
      var camposPlan    = ['modelo_auto', 'precio_auto', 'cantidad_cuotas'];
      var camposGarante = ['garante_nombre', 'garante_dni', 'garante_ingreso',
                           'garante_antiguedad', 'garante_relacion', 'garante_telefono'];
      if (errKeys.some(function (k) { return camposPlan.indexOf(k) >= 0; })) {
        activarTab('plan');
      } else if (errKeys.some(function (k) { return camposGarante.indexOf(k) >= 0; })) {
        activarTab('garante');
      }
    } catch (e) {}
  }


  /* ══════════════════════════════════════════════════════════
     2. SELECCIÓN DE AUTO — bloquea precio y modelo al elegir
  ══════════════════════════════════════════════════════════ */
  var cards = document.querySelectorAll('.car-card');

  function bloquearCamposPlan(model, price) {
    var inputPrecio  = document.getElementById('id_precio_auto');
    var selectModelo = document.getElementById('id_modelo_auto');

    if (inputPrecio) {
      inputPrecio.value = price;
      inputPrecio.setAttribute('readonly', 'readonly');
      inputPrecio.style.background  = 'var(--gray-bg)';
      inputPrecio.style.cursor      = 'not-allowed';
      inputPrecio.style.color       = 'var(--gray-text)';
    }

    if (selectModelo) {
      // Seleccionar la opción correcta
      for (var i = 0; i < selectModelo.options.length; i++) {
        if (selectModelo.options[i].value === model) {
          selectModelo.selectedIndex = i;
          break;
        }
      }
      // Bloquear visualmente SIN usar disabled (disabled no se envía con el form)
      selectModelo.style.pointerEvents = 'none';
      selectModelo.style.background    = 'var(--gray-bg)';
      selectModelo.style.color         = 'var(--gray-text)';
    }
  }

  function desbloquearCamposPlan() {
    var inputPrecio  = document.getElementById('id_precio_auto');
    var selectModelo = document.getElementById('id_modelo_auto');

    if (inputPrecio) {
      inputPrecio.removeAttribute('readonly');
      inputPrecio.style.background = '';
      inputPrecio.style.cursor     = '';
      inputPrecio.style.color      = '';
    }
    if (selectModelo) {
      selectModelo.style.pointerEvents = '';
      selectModelo.style.background    = '';
      selectModelo.style.color         = '';
    }
  }

  cards.forEach(function (card) {
    var btn = card.querySelector('.car-select-btn');
    if (!btn) return;

    btn.addEventListener('click', function () {

      // 1. Reset visual de todas las cards + desbloquear campos
      cards.forEach(function (c) {
        c.classList.remove('car-card--selected');
        var b   = c.querySelector('.car-select-btn');
        var chk = c.querySelector('.car-check');
        if (b)   { b.classList.remove('btn--selected'); b.classList.add('btn--outline'); b.textContent = 'Seleccionar'; }
        if (chk) chk.remove();
      });
      desbloquearCamposPlan();

      // 2. Marcar esta card
      card.classList.add('car-card--selected');
      btn.classList.remove('btn--outline');
      btn.classList.add('btn--selected');
      btn.textContent = 'Seleccionado';

      var chk = document.createElement('div');
      chk.className   = 'car-check';
      chk.textContent = '✓';
      card.prepend(chk);

      var model = card.dataset.model;
      var price = card.dataset.price;
      var img   = card.dataset.img;

      // 3. Cargar y bloquear precio + modelo
      bloquearCamposPlan(model, price);

      // 4. Actualizar panel de informe lateral
      var elName  = document.getElementById('informe-car-name');
      var elPrice = document.getElementById('informe-car-price');
      var elImg   = document.getElementById('informe-car-img');

      if (elName)  elName.textContent  = model;
      if (elPrice) elPrice.textContent = '$' + parseInt(price).toLocaleString('es-AR');
      if (elImg && img) {
        elImg.src           = img;
        elImg.alt           = model;
        elImg.style.display = 'block';
      }

      // 5. Disparar evento input para actualizar hint dólar e informe dinámico
      var inputPrecio = document.getElementById('id_precio_auto');
      if (inputPrecio) inputPrecio.dispatchEvent(new Event('input'));

      actualizarInforme();
    });
  });


  /* ══════════════════════════════════════════════════════════
     3. COTIZACIÓN DEL DÓLAR
  ══════════════════════════════════════════════════════════ */
  var cotizacionDolar = null;

  fetch('/api/cotizacion-dolar/')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.ok) {
        cotizacionDolar = parseFloat(data.venta);
        var hiddenInput = document.getElementById('cotizacion_dolar_input');
        if (hiddenInput) hiddenInput.value = cotizacionDolar;
      }
    })
    .catch(function () {});

  function mostrarHintDolar(inputId, infoId) {
    var inputEl = document.getElementById(inputId);
    var infoEl  = document.getElementById(infoId);
    if (!inputEl || !infoEl) return;

    inputEl.addEventListener('input', function () {
      var valor = parseFloat(inputEl.value);
      if (!cotizacionDolar || !valor || valor <= 0) {
        infoEl.textContent = '';
        return;
      }
      var usd = (valor / cotizacionDolar).toFixed(2);
      infoEl.textContent =
        'Este importe equivale a ' + Number(usd).toLocaleString('es-AR') +
        ' dólares bajo la cotización del dólar oficial del día ($' +
        cotizacionDolar.toLocaleString('es-AR') + ').';
    });
  }

  mostrarHintDolar('id_precio_auto',     'info-precio');
  mostrarHintDolar('id_ingreso_mensual', 'info-ingreso');
  mostrarHintDolar('id_garante_ingreso', 'info-garante-ingreso');


  /* ══════════════════════════════════════════════════════════
     4. INFORME DINÁMICO (panel lateral derecho)
  ══════════════════════════════════════════════════════════ */
  function formatPesos(n) {
    return n > 0
      ? '$' + Number(n).toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
      : '—';
  }

  function actualizarInforme() {
    var precio   = parseFloat((document.getElementById('id_precio_auto')     || {}).value) || 0;
    var cuotas   = parseInt  ((document.getElementById('id_cantidad_cuotas') || {}).value) || 0;
    var ingreso  = parseFloat((document.getElementById('id_ingreso_mensual') || {}).value) || 0;
    var gIngreso = parseFloat((document.getElementById('id_garante_ingreso') || {}).value) || 0;

    var elCuotas  = document.getElementById('informe-cuotas');
    var elIngreso = document.getElementById('informe-ingreso');
    var elGarante = document.getElementById('informe-garante-ingreso');
    var elCuota   = document.getElementById('informe-cuota');
    var elPct     = document.getElementById('informe-porcentaje');

    if (elCuotas)  elCuotas.textContent  = cuotas  || '—';
    if (elIngreso) elIngreso.textContent = formatPesos(ingreso);
    if (elGarante) elGarante.textContent = formatPesos(gIngreso);

    if (precio > 0 && cuotas > 0) {
      var cuota = precio / cuotas;
      if (elCuota) elCuota.textContent = formatPesos(cuota);
      if (elPct)   elPct.textContent   = ingreso > 0
        ? ((cuota / ingreso) * 100).toFixed(2) + '%'
        : '—';
    } else {
      if (elCuota) elCuota.textContent = '—';
      if (elPct)   elPct.textContent   = '—';
    }
  }

  // Escuchar cambios en todos los campos que afectan el informe
  ['id_precio_auto', 'id_cantidad_cuotas', 'id_ingreso_mensual', 'id_garante_ingreso'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.addEventListener('input',  actualizarInforme);
      el.addEventListener('change', actualizarInforme);
    }
  });

  // Ejecutar una vez al cargar por si Django repopuló el form con valores previos
  actualizarInforme();


  /* ══════════════════════════════════════════════════════════
     5. DRAWER (menú hamburguesa)
  ══════════════════════════════════════════════════════════ */
  var menuBtn  = document.querySelector('.navbar__menu');
  var drawer   = document.getElementById('drawer');
  var overlay  = document.getElementById('drawerOverlay');
  var closeBtn = document.getElementById('drawerClose');

  function abrirDrawer()  {
    if (drawer)  drawer.classList.add('drawer--open');
    if (overlay) overlay.classList.add('drawer-overlay--visible');
    if (menuBtn) menuBtn.classList.add('navbar__menu--active');
  }
  function cerrarDrawer() {
    if (drawer)  drawer.classList.remove('drawer--open');
    if (overlay) overlay.classList.remove('drawer-overlay--visible');
    if (menuBtn) menuBtn.classList.remove('navbar__menu--active');
  }

  if (menuBtn)  menuBtn.addEventListener('click',  abrirDrawer);
  if (closeBtn) closeBtn.addEventListener('click', cerrarDrawer);
  if (overlay)  overlay.addEventListener('click',  cerrarDrawer);


  /* ══════════════════════════════════════════════════════════
     6. VALIDACIÓN DE EDAD (cliente) — 18 mín, máx 78 al finalizar
  ══════════════════════════════════════════════════════════ */
  var formSimulacion = document.getElementById('formSimulacion');
  if (formSimulacion) formSimulacion.addEventListener('submit', function (e) {
  var erroresCliente = [];

  // Validar edad del titular
  var inputFecha = document.getElementById('id_fecha_nacimiento');
  if (inputFecha && inputFecha.value) {
    var nac  = new Date(inputFecha.value);
    var hoy  = new Date();
    var edad = hoy.getFullYear() - nac.getFullYear();
    var m = hoy.getMonth() - nac.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) edad--;
    var cuotasEl = document.getElementById('id_cantidad_cuotas');
    var cuotas   = cuotasEl ? parseInt(cuotasEl.value) || 84 : 84;

    if (edad < 18) {
      erroresCliente.push({ campo: 'error-fecha-nacimiento',
        msg: 'Debés tener al menos 18 años.' });
    } else if (edad + cuotas / 12 > 78) {
      erroresCliente.push({ campo: 'error-fecha-nacimiento',
        msg: 'Al finalizar el plan superarías los 78 años permitidos.' });
    }
  }

  // Si hay errores del cliente, mostrarlos TODOS y detener el envío
  if (erroresCliente.length > 0) {
    e.preventDefault();
    erroresCliente.forEach(function(err) {
      var el = document.getElementById(err.campo);
      if (el) { el.textContent = err.msg; el.style.display = 'block'; }
    });
    // Navegar al primer tab con error
    activarTab('personal');
  }
  });
  /* ══════════════════════════════════════════════════════════
     7. LOGIN / REGISTRO
     Solo se ejecuta si la página tiene la card de autenticación
  ══════════════════════════════════════════════════════════ */
  if (!document.querySelector('.auth-card')) return;

  function activarTabAuth(id) {
    document.querySelectorAll('.auth-tab').forEach(function (t) {
      t.classList.toggle('active', t.dataset.tab === id);
    });
    document.querySelectorAll('.auth-panel').forEach(function (p) {
      p.classList.toggle('active', p.id === 'panel-' + id);
    });
  }

  document.querySelectorAll('.auth-tab').forEach(function (t) {
    t.addEventListener('click', function () { activarTabAuth(this.dataset.tab); });
  });
  document.querySelectorAll('.auth-switch-btn').forEach(function (b) {
    b.addEventListener('click', function () { activarTabAuth(this.dataset.switch); });
  });

  var tabParam = new URLSearchParams(window.location.search).get('tab');
  if (tabParam) activarTabAuth(tabParam);

  document.querySelectorAll('.pw-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var inp = document.getElementById(this.dataset.target);
      if (!inp) inp = this.closest('.af-wrap').querySelector('input');
      if (!inp) return;
      inp.type = inp.type === 'password' ? 'text' : 'password';
      var eyeOn  = this.querySelector('.eye-on');
      var eyeOff = this.querySelector('.eye-off');
      if (eyeOn)  eyeOn.style.display  = inp.type === 'password' ? '' : 'none';
      if (eyeOff) eyeOff.style.display = inp.type === 'password' ? 'none' : '';
    });
  });

  var pw1 = document.getElementById('id_password1');
  if (pw1) {
    pw1.addEventListener('input', function () {
      var v    = this.value;
      var wrap = document.getElementById('strengthWrap');
      var fill = document.getElementById('strengthFill');
      var lbl  = document.getElementById('strengthLbl');
      if (!wrap) return;
      wrap.style.display = v ? '' : 'none';
      var score = 0;
      if (v.length >= 8)           score++;
      if (/[A-Z]/.test(v))         score++;
      if (/[0-9]/.test(v))         score++;
      if (/[^A-Za-z0-9]/.test(v))  score++;
      fill.style.width      = ['0%','25%','50%','75%','100%'][score];
      fill.style.background = ['','#e07070','#e0a870','#d4c24a','#52d681'][score] || '#e07070';
      lbl.textContent       = ['','Muy débil','Regular','Buena','Excelente'][score] || '';
    });
  }

  ['loginForm', 'registerForm'].forEach(function (formId) {
    var form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', function () {
      var btnId = formId === 'loginForm' ? 'loginBtn' : 'registerBtn';
      var btn   = document.getElementById(btnId);
      if (btn) {
        btn.disabled = true;
        var txtEl  = btn.querySelector('.btn-txt');
        var loadEl = btn.querySelector('.btn-load');
        if (txtEl)  txtEl.style.display  = 'none';
        if (loadEl) loadEl.style.display = 'flex';
      }
    });
  });

});