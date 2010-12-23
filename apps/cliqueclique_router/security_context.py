import django.shortcuts
import django.template
import django.core.urlresolvers
import django.utils.simplejson
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import django.http
import utils.smime
import utils.hash
import django.contrib.auth.decorators
import cliqueclique_router.server
import settings

def load_security_contexts(request):
    if 'security_contexts' in request.session:
        return django.utils.simplejson.loads(request.session['security_contexts'])
    else:
        default_key = utils.hash.rand_id()
        return {
            'free': range(1, len(settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS)),
            'used': {default_key: {'address_idx': 0, 'children': []}},
            'default': default_key
            }

def save_security_contexts(request, security_contexts):
    request.session.security_contexts = django.utils.simplejson.dumps(security_contexts)


def create_security_context(request, parent_key):
    security_contexts = load_security_contexts(request)

    if parent_key is not None:
        assert parent_key in security_contexts['used']

    context_address_idx = security_contexts['free'].pop()
    context_key = utils.hash.rand_id()
    context_delete_key = utils.hash.rand_id()
    security_contexts['used'][context_key] = {'address_idx': context_address_idx, 'delete_key': context_delete_key, 'children': []}

    if parent_key is not None:
        security_contexts['used'][parent_key]['children'].append(context_key)

    save_security_contexts(request, security_contexts)

    return {'key': context_key, 'delete_key': context_delete_key, 'address': settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS[context_address_idx]}

def get_security_context(request, key):
    security_contexts = load_security_contexts(request)    
    if key is None:
        key = security_contexts['default']
    context = security_contexts['used'][key]
    return {'key': key, 'address': settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS[context['address_idx']]}

def delete_security_context(request, key, delete_key):
    security_contexts = load_security_contexts(request)

    context = security_contexts['used'][key]
    if delete_key is not None:
        assert context['delete_key'] == delete_key

    def delete_context(key):
        context = security_contexts['used'][key]
        del security_contexts['used'][key]
        security_contexts['free'].append(context['address_idx'])
 
        for child in context['children']:
            delete_context(child)

    delete_context(key)

    save_security_contexts(request, security_contexts)

def context_processor(request):
    return {'security_context': get_security_context(request, None)}
