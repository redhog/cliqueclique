import django.contrib.admin
import cliqueclique_subscription.models

django.contrib.admin.site.register(cliqueclique_subscription.models.BaseDocumentSubscription)
django.contrib.admin.site.register(cliqueclique_subscription.models.DocumentSubscription)
