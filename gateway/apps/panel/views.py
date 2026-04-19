from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from apps.tenants.models import Negocio


def panel_login(request):
    primer_arranque = not User.objects.filter(is_superuser=True).exists()

    if not primer_arranque and request.user.is_authenticated:
        return redirect('panel:dashboard')

    if request.method == 'POST':
        if primer_arranque:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            confirm  = request.POST.get('confirm', '')
            if not username or not password:
                messages.error(request, 'Usuario y contraseña son requeridos.')
            elif password != confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
            else:
                User.objects.create_superuser(username=username, password=password, email='')
                user = authenticate(request, username=username, password=password)
                login(request, user)
                messages.success(request, f'Cuenta "{username}" creada. ¡Bienvenido!')
                return redirect('panel:dashboard')
        else:
            user = authenticate(
                request,
                username=request.POST.get('username'),
                password=request.POST.get('password'),
            )
            if user and user.is_superuser:
                login(request, user)
                return redirect('panel:dashboard')
            messages.error(request, 'Credenciales inválidas o sin permisos de superusuario.')

    return render(request, 'panel/login.html', {'primer_arranque': primer_arranque})


def panel_logout(request):
    logout(request)
    return redirect('panel:login')


@login_required(login_url='/panel/login/')
def dashboard(request):
    negocios = Negocio.objects.all()
    return render(request, 'panel/dashboard.html', {'negocios': negocios})


@login_required(login_url='/panel/login/')
def negocio_nuevo(request):
    if request.method == 'POST':
        negocio = _save_negocio(None, request.POST)
        messages.success(request, f'Negocio "{negocio.nombre}" creado correctamente.')
        return redirect('panel:negocio_editar', pk=negocio.pk)
    return render(request, 'panel/negocio_form.html', {'negocio': None})


@login_required(login_url='/panel/login/')
def negocio_editar(request, pk):
    negocio = get_object_or_404(Negocio, pk=pk)
    if request.method == 'POST':
        _save_negocio(negocio, request.POST)
        messages.success(request, 'Cambios guardados.')
        return redirect('panel:negocio_editar', pk=pk)
    return render(request, 'panel/negocio_form.html', {'negocio': negocio})


@login_required(login_url='/panel/login/')
def negocio_toggle(request, pk):
    negocio = get_object_or_404(Negocio, pk=pk)
    negocio.activo = not negocio.activo
    negocio.save(update_fields=['activo'])
    estado = 'activado' if negocio.activo else 'desactivado'
    messages.success(request, f'Negocio "{negocio.nombre}" {estado}.')
    return redirect('panel:dashboard')


def _save_negocio(negocio, data):
    """Create or update a Negocio from POST data."""
    is_new = negocio is None
    if is_new:
        negocio = Negocio()

    # Basic info
    negocio.nombre = data.get('nombre', negocio.nombre if not is_new else '')
    negocio.razon_social = data.get('razon_social') or None
    negocio.cuit = data.get('cuit') or None
    negocio.telefono = data.get('telefono') or None
    negocio.direccion = data.get('direccion') or None
    negocio.sitio_web = data.get('sitio_web') or None
    negocio.activo = data.get('activo') == 'on' if is_new else negocio.activo

    # Brand
    negocio.nombre_comercial = data.get('nombre_comercial') or None
    negocio.slogan = data.get('slogan') or None
    negocio.icono_emoji = data.get('icono_emoji') or '📦'
    negocio.logo_url = data.get('logo_url') or None
    negocio.color_primario = data.get('color_primario') or '#4f46e5'
    negocio.color_secundario = data.get('color_secundario') or '#7c3aed'
    negocio.email_soporte = data.get('email_soporte') or None
    negocio.texto_footer = data.get('texto_footer') or None

    # Email
    negocio.smtp_host = data.get('smtp_host') or None
    negocio.smtp_port = int(data.get('smtp_port') or 587)
    negocio.smtp_user = data.get('smtp_user') or None
    negocio.smtp_from = data.get('smtp_from') or None
    if data.get('smtp_pass'):
        negocio.smtp_pass = data['smtp_pass']
    if data.get('resend_api_key'):
        negocio.resend_api_key = data['resend_api_key']

    # Pagos
    if data.get('mp_access_token'):
        negocio.mp_access_token = data['mp_access_token']
    negocio.webhook_notificacion = data.get('webhook_notificacion') or None

    # Logística
    if data.get('envia_token'):
        negocio.envia_token = data['envia_token']
    negocio.envia_ambiente = data.get('envia_ambiente') or 'TEST'

    # WhatsApp
    negocio.whatsapp_provider = data.get('whatsapp_provider') or None
    if data.get('whatsapp_api_key'):
        negocio.whatsapp_api_key = data['whatsapp_api_key']
    negocio.whatsapp_number = data.get('whatsapp_number') or None

    negocio.save()
    return negocio
