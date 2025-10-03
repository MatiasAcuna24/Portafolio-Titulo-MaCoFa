from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.utils.html import strip_tags

def _send_html_mail(subject, to_email, template_name, context, reply_to=None):
    ctx = {"year": timezone.now().year}
    ctx.update(context or {})

    html_content = render_to_string(template_name, ctx)
    text_content = strip_tags_fallback(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        reply_to=[reply_to] if reply_to else None,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

def strip_tags_fallback(html):
    # Minimal fallback para texto plano
    import re
    text = re.sub(r"<br\s*/?>", "\n", html)
    return re.sub(r"<[^>]+>", "", text)

def send_welcome_email(user):
    subject = "¡Bienvenid@ a Dulce Arte!"
    _send_html_mail(
        subject,
        user.email,
        "emails/welcome.html",
        {"user": user},
    )

def send_order_confirmation(user, pedido):
    items = pedido.items.select_related("producto").all()

    subject = f"🍰 Pedido confirmado – {pedido.numero}"
    html_content = render_to_string("emails/order_confirmation.html", {
        "user": user,
        "pedido": pedido,
        "items": items
    })
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

def send_order_status_update(user, pedido, estado, mensaje_extra=None):
    subject = f"📦 Tu pedido {pedido.numero} ahora está: {estado.title()}"
    html_content = render_to_string("emails/order_status_update.html", {
        "user": user,
        "pedido": pedido,
        "estado": estado,
        "mensaje_extra": mensaje_extra
    })
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)