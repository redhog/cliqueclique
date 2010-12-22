import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import django.http
import utils.smime
import django.contrib.auth.decorators
import cliqueclique_router.server
import fcdjangoutils.jsonview

@fcdjangoutils.jsonview.json_view
def close(request):
    cliqueclique_router.server.Webserver.close(request.GET['key'])
    return {'closed': True} # Not gonna happen, web server is already down...
