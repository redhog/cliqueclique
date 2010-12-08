import django.contrib.admin
import cliqueclique_subscription.models

django.contrib.admin.site.register(cliqueclique_subscription.models.DocumentSubscription)

class PeerDocumentSubscriptionAdmin(django.contrib.admin.ModelAdmin):
    fieldsets = [("The subscription of the peer",
                  {'fields': ('serial',
                              'is_subscribed',
                              'center_node_is_subscribed',
                              'center_node_id',
                              'center_distance',
                              'has_copy')}),
                 ("Sync metadata",
                  {'fields': ('local_serial',
                              'local_resend_interval',
                              'local_resend_time',
                              'peer_send')}),
                 ('Subscription metadata',
                  {'fields': ('peer',
                              'local_subscription')}),
                 ]

    list_display_links = list_display = (
        'peer',
        'local_subscription',
        'local_serial',
        'serial',
        'is_subscribed',
        'center_node_is_subscribed',
        'center_node_id',
        'center_distance',
        'has_copy')
    search_fields = ()


django.contrib.admin.site.register(cliqueclique_subscription.models.PeerDocumentSubscription, PeerDocumentSubscriptionAdmin)
