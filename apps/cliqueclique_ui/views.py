import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import django.http
import utils.smime
import utils.djangosmime
import django.contrib.auth.decorators
import fcdjangoutils.jsonview

@django.contrib.auth.decorators.login_required
def ui(request):
    return django.shortcuts.render_to_response(
        'cliqueclique_ui/ui.html',
        context_instance=django.template.RequestContext(request))
