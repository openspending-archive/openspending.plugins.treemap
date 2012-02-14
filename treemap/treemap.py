import logging

from pylons import tmpl_context as c

from genshi.filters import Transformer
from genshi.input import HTML

from openspending.lib import json
#from openspending.ui.lib.color import color_range, parent_color
from openspending.plugins.core import SingletonPlugin, implements
from openspending.plugins.interfaces import IGenshiStreamFilter

log = logging.getLogger(__name__)

JS_SNIPPET = """
<!-- OpenSpending Treemap Plugin includes -->
<!--[if IE]><script language="javascript" type="text/javascript" src="/js/excanvas.js"></script><![endif]-->

<script src="http://assets.openspending.org/openspendingjs/master/lib/vendor/underscore.js"></script>
<script type="text/javascript" src="http://assets.openspending.org/openspendingjs/master/lib/aggregator.js"></script>
<script type="text/javascript" src="http://assets.openspending.org/openspendingjs/master/lib/utils/utils.js"></script>
<script type="text/javascript" src="http://assets.openspending.org/openspendingjs/master/lib/utils/utils.js"></script>
<script type="text/javascript" src="http://assets.openspending.org/openspendingjs/master/app/treemap/js/thejit-2.js"></script>
<script type="text/javascript" src="http://assets.openspending.org/openspendingjs/master/app/treemap/js/treemap.js"></script>

<script>
  (function ($) {
    $(function () {
      var db = new OpenSpending.TreeMap($('#mainvis'));
      new OpenSpending.Aggregator({
        apiUrl: '%(endpoint)s',
        dataset: '%(dataset)s',
        drilldowns: ['%(drilldown)s'],
        cuts: %(cuts)s,
        rootNodeLabel: 'Total', 
        callback: function(data) {
          db.setDataFromAggregator(this.dataset, this.drilldowns[0], data);
          db.draw();
        }
      });
    })
  })(jQuery)
</script>

"""

CSS_SNIPPET = """
<link rel="stylesheet" type="text/css"
      href="http://assets.openspending.org/openspendingjs/master/app/treemap/css/treemap.css" />
<style>
    #mainvis {
        height: 400px;
        margin-top: -2em;
    }
</style>
"""

BODY_SNIPPET = """
<div id='mainvis' class='treemap'>&nbsp;</div><br/>
"""

class TreemapPlugin(SingletonPlugin):
    implements(IGenshiStreamFilter, inherit=True)

    def filter(self, stream):
        if hasattr(c, 'viewstate') and hasattr(c, 'time'):
            if len(c.viewstate.aggregates) > 1:
                opts = {
                        'dataset': c.dataset.name,
                        'drilldown': c.view.drilldown,
                        'endpoint': '/api',
                        'cuts': json.dumps(['year:' + c.time] + \
                            ['%s:%s' % d for d in c.view.cuts])
                    }
                stream = stream | Transformer('html/body')\
                   .append(HTML(JS_SNIPPET % opts))
                stream = stream | Transformer('html/head')\
                   .append(HTML(CSS_SNIPPET))
                stream = stream | Transformer('//div[@id="vis"]')\
                    .append(HTML(BODY_SNIPPET))
        return stream

