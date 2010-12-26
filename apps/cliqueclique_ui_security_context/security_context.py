import django.shortcuts
import django.template
import django.core.urlresolvers
import django.utils.simplejson
import django.http
import django.contrib.auth.decorators
import utils.hash
import settings

def load_security_contexts(request):
    if 'security_contexts' in request.session:
        return django.utils.simplejson.loads(request.session['security_contexts'])
    else:
        default_key = utils.hash.rand_id()
        server_key = utils.hash.rand_id()
        security_contexts = {
            'free': range(1, len(settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS)),
            'used': {default_key: {'key': default_key,
                                   'address_idx': 0,
                                   'children': [],
                                   'server_key': server_key,
                                   'owner_document_id': None}},
            'idx': {'0': default_key}
            }
        save_security_contexts(request, security_contexts)
        return security_contexts

def save_security_contexts(request, security_contexts):
    print "SAVE", request.session.items()
    request.session['security_contexts'] = django.utils.simplejson.dumps(security_contexts)
    request.session.save()

def create_security_context(request, parent_key, owner_document_id):
    security_contexts = load_security_contexts(request)

    if parent_key is not None:
        assert parent_key in security_contexts['used']

    context_address_idx = security_contexts['free'].pop()
    context_key = utils.hash.rand_id()
    server_key = utils.hash.rand_id()
    security_contexts['used'][context_key] = {
        'key': context_key,
        'address_idx': context_address_idx,
        'children': [],
        'server_key': server_key,
        'owner_document_id': owner_document_id}
    security_contexts['idx'][str(context_address_idx)] = context_key

    if parent_key is not None:
        security_contexts['used'][parent_key]['children'].append(context_key)

    save_security_contexts(request, security_contexts)

    return {'key': context_key, 'address': settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS[context_address_idx]}

def get_security_context_obj(request, key = None, address = None):
    security_contexts = load_security_contexts(request)    
    if key is None:
        if address is None:
            address = request.environ['HTTP_HOST']
        key = security_contexts['idx'][str(settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS.index(address))]
    return security_contexts['used'][key]

def get_security_context(request, key = None, address = None):
    context = get_security_context_obj(request, key, address)
    return {'key': context['key'],
            'address': settings.CLIQUECLIQUE_UI_SECURITY_CONTEXTS[context['address_idx']],
            'owner_document_id': context['owner_document_id']}

def get_server_key(request, key = None, address = None):
    context = get_security_context_obj(request, key, address)
    return context['server_key']

def delete_security_context(request, key):
    security_contexts = load_security_contexts(request)

    def delete_context(key):
        context = security_contexts['used'][key]
        del security_contexts['used'][key]
        del security_contexts['idx'][str(context['address_idx'])]
        security_contexts['free'].append(context['address_idx'])
 
        for child in context['children']:
            delete_context(child)

    delete_context(key)

    save_security_contexts(request, security_contexts)

def context_processor(request):
    return {'security_context': get_security_context(request)}

