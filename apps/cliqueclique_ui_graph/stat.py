import numpy
import matplotlib
matplotlib.use("cairo")
import matplotlib.mlab
import matplotlib.pyplot
import StringIO
import cliqueclique_document.models
import cliqueclique_subscription.models

class DocumentGraph(object):
    def __init__(self, document_id, attr = "peer_nrs"):
        data = numpy.array([
                getattr(sub, attr)
                for sub
                in cliqueclique_subscription.models.DocumentSubscription.objects.filter(document__document_id = document_id).all()])

        n, bins, patches = matplotlib.pyplot.hist(data, data.max(), facecolor='green', alpha=0.75)

        matplotlib.pyplot.xlabel(attr)
        matplotlib.pyplot.ylabel('count')
        #matplotlib.pyplot.title(document_id)

        matplotlib.pyplot.axis([0.0, data.max(), 0.0, max(n)])
        matplotlib.pyplot.grid(True)

    def create_png(self):
        tmpfile = StringIO.StringIO()
        matplotlib.pyplot.savefig(tmpfile, format="png")
        matplotlib.pyplot.clf()
        return tmpfile.getvalue()
