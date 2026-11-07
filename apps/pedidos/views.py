from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.catalogo.models import Paquete
from apps.usuarios.models import Usuario
from apps.pedidos.models import Reserva, Pago
from apps.usuarios.views import login_requerido_custom

MIN_ACTIVIDADES = 3
MAX_ACTIVIDADES = 5
MIN_HOTELES = 1
MAX_HOTELES = 1
MIN_VUELOS = 1
MAX_VUELOS = 1

def _obtener_carrito(request):
    return request.session.setdefault('carrito', {})

def _validar_seleccion(datos, campo, opciones, min_deseado, maximo, etiqueta, singular=None):
    total = opciones.count()
    if total == 0:
        return [], None

    minimo = min(min_deseado, total)
    ids = {int(x) for x in datos.getlist(campo) if x.isdigit()}

    if not (minimo <= len(ids) <= maximo):
        if minimo == maximo == 1 and singular:
            return None, f"Elige 1 {singular}."
        return None, f"Elige entre {minimo} y {maximo} {etiqueta}."

    elegidos = list(opciones.filter(id__in=ids))
    if len(elegidos) != len(ids):
        return None, f"La selección de {etiqueta} no es válida."

    return elegidos, None

def carrito_ver(request):
    carrito = _obtener_carrito(request)
    subtotal = sum(item['subtotal'] for item in carrito.values())
    iva = int(subtotal * 0.19)
    total = subtotal + iva
    return render(request, 'pedidos/carrito.html', {
        'items_carrito': carrito.values(),
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
        'esta_vacio': len(carrito) == 0,
    })

def carrito_agregar(request, id):
    paquete = get_object_or_404(Paquete, id=id)
    carrito = _obtener_carrito(request)
    str_id = str(paquete.id)

    datos = request.POST if request.method == 'POST' else request.GET
    sin_seleccion = (not datos.getlist('actividades') and not datos.getlist('hoteles') and not datos.getlist('vuelos'))

    if str_id in carrito and sin_seleccion:
        actividades_carrito = carrito[str_id].get('actividades', [])
        hoteles_carrito = carrito[str_id].get('hoteles', [])
        vuelos_carrito = carrito[str_id].get('vuelos', [])
    else:
        actividades, error = _validar_seleccion(
            datos, 'actividades', paquete.itinerarios.order_by('dia', 'horario'),
            MIN_ACTIVIDADES, MAX_ACTIVIDADES, 'actividades')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        hoteles, error = _validar_seleccion(
            datos, 'hoteles', paquete.hoteles.order_by('nombre'),
            MIN_HOTELES, MAX_HOTELES, 'hoteles', singular='hotel')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        vuelos, error = _validar_seleccion(
            datos, 'vuelos', paquete.vuelos.order_by('fecha_salida', 'hora_salida'),
            MIN_VUELOS, MAX_VUELOS, 'vuelos', singular='vuelo')
        if error:
            messages.warning(request, f"{error} Paquete '{paquete.nombre}'.")
            return redirect('catalogo:detalle', paquete.id)

        actividades_carrito = [{'id': a.id, 'nombre': a.actividad} for a in actividades]
        hoteles_carrito = [{'id': h.id, 'nombre': h.nombre, 'ciudad': h.ciudad} for h in hoteles]
        vuelos_carrito = [{'id': f.id, 'nombre': f.aerolinea, 'ruta': f"{f.ciudad_origen} → {f.ciudad_destino}"} for f in vuelos]

    cantidad_actual = carrito.get(str_id, {}).get('cantidad', 0)
    nueva_cantidad = cantidad_actual + 1

    if nueva_cantidad > paquete.cupos_disponibles:
        messages.warning(request, f"Límite de cupos alcanzado ({paquete.cupos_disponibles} disponibles) para '{paquete.nombre}'.")
        return redirect('pedidos:ver')

    carrito[str_id] = {
        'id': paquete.id,
        'nombre': paquete.nombre,
        'precio': int(paquete.precio_paquete),
        'cantidad': nueva_cantidad,
        'subtotal': int(paquete.precio_paquete) * nueva_cantidad,
        'actividades': actividades_carrito,
        'hoteles': hoteles_carrito,
        'vuelos': vuelos_carrito,
    }

    request.session.modified = True
    messages.success(request, f"Paquete '{paquete.nombre}' añadido a las reservas.")
    return redirect(request.META.get('HTTP_REFERER') or 'pedidos:ver')

def carrito_restar(request, id):
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        carrito[str_id]['cantidad'] -= 1
        if carrito[str_id]['cantidad'] <= 0:
            del carrito[str_id]
        else:
            carrito[str_id]['subtotal'] = carrito[str_id]['precio'] * carrito[str_id]['cantidad']
        request.session.modified = True
    return redirect('pedidos:ver')

def carrito_eliminar(request, id):
    carrito = _obtener_carrito(request)
    str_id = str(id)
    if str_id in carrito:
        del carrito[str_id]
        request.session.modified = True
        messages.warning(request, "Paquete eliminado de la lista de reservas.")
    return redirect('pedidos:ver')

def carrito_limpiar(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    return redirect('pedidos:ver')

@login_requerido_custom
def checkout_simulado(request):
    if request.method == 'POST':
        carrito = _obtener_carrito(request)
        if not carrito:
            return redirect('catalogo:lista')

        usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])

        subtotal = sum(item['subtotal'] for item in carrito.values())
        iva = int(subtotal * 0.19)
        total = subtotal + iva
        items_comprados = list(carrito.values())

        for item in items_comprados:
            paquete = get_object_or_404(Paquete, id=item['id'])

            valor_con_iva = item['subtotal'] + int(item['subtotal'] * 0.19)

            reserva = Reserva.objects.create(
                usuario=usuario,
                paquete=paquete,
                estado='Pagada',
                precio_total=valor_con_iva
            )

            ids_actividades = [a['id'] for a in item.get('actividades', [])]
            if ids_actividades:
                reserva.actividades.set(paquete.itinerarios.filter(id__in=ids_actividades))

            ids_hoteles = [h['id'] for h in item.get('hoteles', [])]
            if ids_hoteles:
                reserva.hoteles.set(paquete.hoteles.filter(id__in=ids_hoteles))

            ids_vuelos = [f['id'] for f in item.get('vuelos', [])]
            if ids_vuelos:
                reserva.vuelos.set(paquete.vuelos.filter(id__in=ids_vuelos))

            Pago.objects.create(
                reserva=reserva,
                monto=valor_con_iva,
                metodo_pago='Webpay Simulador',
                estado_transaccion='Aprobada'
            )

            if paquete.cupos_disponibles >= item['cantidad']:
                paquete.cupos_disponibles -= item['cantidad']
                paquete.save()

        del request.session['carrito']
        request.session.modified = True

        return render(request, 'pedidos/checkout_exito.html', {
            'items': items_comprados,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'orden_id': f"RES-{usuario.id}-2026",
        })

    return redirect('pedidos:ver')