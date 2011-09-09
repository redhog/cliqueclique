import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_node.models
import cliqueclique_mime.models
import cliqueclique_document.models
import cliqueclique_subscription.models
import cliqueclique_ui_security_context.security_context
import email
import email.mime.text
import django.http
import utils.hash
import utils.smime
import utils.djangosmime
import django.contrib.auth.decorators
import fcdjangoutils.jsonview
import sys
import traceback
import jogging
import os.path
import settings

def json_view_or_redirect(fn):
    def json_view_or_redirect(request, *arg, **kw):
        redirect = None
        if 'redirect' in request.GET:
            redirect = request.GET['redirect']
        elif 'redirect' in request.POST:
            redirect = request.POST['redirect']

        if redirect:
            res = fn(request, *arg, **kw)
            return django.shortcuts.redirect(redirect % res)
        else:
            return fcdjangoutils.jsonview.json_view(fn)(request, *arg, **kw)
    return json_view_or_redirect

def json_error_on_format(fn):
    def json_error_on_format(request, format, *arg, **kw):
        try:
            return fn(request, format, *arg, **kw)
        except django.core.servers.basehttp.WSGIServerException:
            raise
        except Exception, e:
            if settings.CLIQUECLIQUE_DEBUG_JSON_EXCEPTIONS:
                import traceback
                traceback.print_exc()

            etype = sys.modules[type(e).__module__].__name__ + "." + type(e).__name__
            jogging.logging.error("%s: %s" % (str(e), etype))
            if format != 'json':
                raise
            res = {'error': {'type': etype,
                             'description': str(e),
                             'traceback': traceback.format_exc()}}
            res = django.utils.simplejson.dumps(res, default=fcdjangoutils.jsonview.JsonEncodeRegistry().jsonify)
            return django.http.HttpResponse(res, mimetype="text/plain")
    return json_error_on_format

@json_view_or_redirect
@django.contrib.auth.decorators.login_required
def import_document(request):
    if 'document' in request.GET:
        doc = request.GET['document']
    elif 'document' in request.POST:
        doc = request.POST['document']
    elif 'document' in request.FILES:
        doc = request.FILES['document']

    request.user.node.receive(doc)
    doc = utils.smime.message_from_anything(doc)
    container_doc = doc.get_payload()[0]
    update_doc = container_doc.get_payload()[0]    

    return {'document_id': update_doc['document_id']}

@json_view_or_redirect
@django.contrib.auth.decorators.login_required
def post(request):
    if 'document' in request.GET:
        doc = request.GET['document']
    elif 'document' in request.POST:
        doc = request.POST['document']
    elif 'document' in request.FILES:
        doc = request.FILES['document']

    node = request.user.node

    mime = cliqueclique_mime.models.Mime(
        content = fcdjangoutils.jsonview.from_json(
            doc,
            public_key=node.public_key,
            private_key=node.private_key).as_string())
    mime.save()
    doc = cliqueclique_document.models.Document(content = mime)
    doc.save()

    sub = cliqueclique_subscription.models.DocumentSubscription(
        node = node,
        document = doc)
    sub.save()

    for parent in sub.parents.all():
        if not parent.local_is_subscribed:
            parent.local_is_subscribed = True
            parent.save()

    return sub

@json_view_or_redirect
@django.contrib.auth.decorators.login_required
def set_document_local_data(request, document_id):
    if 'local_data' in request.GET:
        content = request.GET['local_data']
    elif 'local_data' in request.POST:
        content = request.POST['local_data']
    elif 'local_data' in request.FILES:
        content = request.FILES['local_data']
    node = request.user.node
    sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = node,
        document__document_id = document_id)
    content = fcdjangoutils.jsonview.from_json(
        content,
        public_key=node.public_key,
        private_key=node.private_key).as_string()
    if sub.local_data is None:
        mime = cliqueclique_mime.models.Mime(subscription = sub)
    else:
        mime = sub.local_data
    mime.content = content,
    mime.save()
    return {'document_id': sub.document.document_id}


@json_error_on_format
@django.contrib.auth.decorators.login_required
def get_document_local_data(request, format, document_id):
    node = request.user.node
    sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = node,
        document__document_id = document_id)

    data = sub.local_data and sub.local_data.content.as_mime or None

    if format == 'mime':
        if not data:
            data = email.mime.multipart.MIMEMultipart()
        data = data.as_string()
        mimetype="text/plain"
    elif format == 'json':
        data = django.utils.simplejson.dumps(data, default=fcdjangoutils.jsonview.JsonEncodeRegistry().jsonify)
        mimetype="text/plain"
    return django.http.HttpResponse(data, mimetype=mimetype)


@json_view_or_redirect
@django.contrib.auth.decorators.login_required
def set_document_flags(request, document_id):
    sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id = document_id)
    for attr in ('bookmarked', 'read', 'local_is_subscribed'):
        if attr in request.POST:
            attrvalue = request.POST[attr]
        elif attr in request.GET:
            attrvalue = request.GET[attr]
        else:
            continue
        if attrvalue == "toggle":
            value = not getattr(sub, attr)
        elif attrvalue == "true":
            value = True
        else:
            value = False
        setattr(sub, attr, value)
    sub.save()
    return {'document_id': sub.document.document_id}

@json_error_on_format
@django.contrib.auth.decorators.login_required
def document(request, format, document_id = None, single = False):
    if document_id and document_id.startswith("local:"):
        # Emulate documents with local files for development. Don't use in production!
        docs = []
        for filename in [os.path.join(settings.CONFIGDIR, "local_documents", document_id[len("local:"):] + ".mime"),
                         os.path.join(settings.PROJECT_ROOT, "local_documents", document_id[len("local:"):] + ".mime")]:
            if os.path.exists(filename):
                with open(filename) as f:
                    data = f.read()
                # This is all fake; we're never commiting
                # anything to the DB, we just do this to be able
                # to serialize it as json or mime or whatever...
                node = request.user.node
                signed = utils.smime.MIMESigned()
                signed.set_cert(node.public_key)
                signed.set_private_key(node.private_key)
                signed.attach(email.message_from_string(data))
                mime = cliqueclique_mime.models.Mime(content = signed.as_string())
                mime.save()
                doc = cliqueclique_document.models.Document(content = mime)
                doc.on_pre_save(None, doc)
                sub = cliqueclique_subscription.models.DocumentSubscription(document = doc)
                sub.node = node
                docs.append(sub)
                break
    else:
        docs = list(cliqueclique_subscription.models.DocumentSubscription.get_by_query(
                q = request.GET.get('query', None),
                node_id = request.user.node.node_id,
                document_id = document_id))

    if format == 'mime':
        if len(docs) == 0:
            docs = email.mime.multipart.MIMEMultipart()
        elif len(docs) == 1:
            docs = docs[0].export()
        else:
            msg = email.mime.multipart.MIMEMultipart()
            for doc in docs:
                msg.attach(doc.send(True))
            docs = docs[0].node.sign(msg)
        docs = docs.as_string()
        mimetype="text/plain"
    elif format == 'json':
        res = {}
        for doc in docs:
            res[doc.document.document_id] = doc
        docs = django.utils.simplejson.dumps(res, default=fcdjangoutils.jsonview.JsonEncodeRegistry().jsonify)
        mimetype="text/plain"
    return django.http.HttpResponse(docs, mimetype=mimetype)

