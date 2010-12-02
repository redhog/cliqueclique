import django.contrib.admin
import cliqueclique_subscription.models

django.contrib.admin.site.register(cliqueclique_subscription.models.DocumentSubscription)

class PeerDocumentSubscriptionAdmin(django.contrib.admin.ModelAdmin):
    fieldsets = [("The subscription of the peer",
                  {'fields': ('peer_old_is_subscribed',
                              'peer_is_subscribed',
                              'peer_center_node_is_subscribed',
                              'peer_center_node_id',
                              'peer_center_distance',
                              'has_copy')}),
                 ("Peers' knowledge about us",
                  {'fields': ('is_subscribed',
                              'center_node_is_subscribed',
                              'center_node_id',
                              'center_distance')}),
                 

                 ('Metadata',
                  {'fields': ('peer',
                              'local_subscription')}),
                 ]

    list_display_links = list_display = (
        'local_subscription',
        'peer',
        'is_dirty')
    search_fields = ()


django.contrib.admin.site.register(cliqueclique_subscription.models.PeerDocumentSubscription, PeerDocumentSubscriptionAdmin)
