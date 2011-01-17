try:
    import json 
except ImportError:
    import simplejson as json

from pylons.i18n import get_lang, _
from genshi.filters import Transformer
from genshi.input import HTML

from wdmmg.lib import helpers as h
from wdmmg.plugins import SingletonPlugin, implements
from wdmmg.plugins import IGenshiStreamFilter 

TITLE_CUTOFF = 0.02

# TODO: Move CSS to its own file. 
HEAD_SNIPPET = """
<!-- wdmmg-treemap includes -->
<script src="/js/thejit-2.js"></script>
<script src="/js/treemap.js"></script>
<script>
$(document).ready(function() {
    init_treemap(%s);
});
</script>
<style>
#treemap {
	position: relative;
	overflow: hidden;
    cursor: pointer;
	color: #fff;
	font-size: 0.8em;
	font-weight: bold; 
}

#treemap h2 {
	font-family: Georgia, serif; 
	font-size: 1.4em;
	color: #fff;
	font-weight: normal;
	margin-bottom: 0.1em;
} 

#_tooltip {
	background-color: #DDE7F0;
	padding: 4px 6px;
	border: 1px solid #A3B3C7;
}
</style>
<!-- wdmmg-treemap end -->
"""

BODY_SNIPPET = """
<div id='treemap' style='width: auto; height: 400px;'>&nbsp;</div><br/>
"""

class TreemapGenshiStreamFilter(SingletonPlugin):
    implements(IGenshiStreamFilter, inherit=True)

    def filter(self, stream):
        from pylons import tmpl_context as c 
        if hasattr(c, 'aggregates') and hasattr(c, 'time'):
            if len(c.aggregates): 
                tree_json = self._generate_tree_json(c.aggregates, c.time, 
                    c.totals.get(c.time, 0))
                stream = stream | Transformer('html/head')\
                    .append(HTML(HEAD_SNIPPET % tree_json))
                stream = stream | Transformer('//div[@id="description"]')\
                    .before(HTML(BODY_SNIPPET))
        return stream 

    def _generate_tree_json(self, aggregates, time, total):
        from wdmmg.lib.helpers import dimension_url, render_value
        fields = []
        for obj, time_values in aggregates:
            value = time_values.get(time)
            if value <= 0: 
                continue
            show_title = (value/max(1,total)) > TITLE_CUTOFF
            field = {'children': [],
                     'id': str(obj.get('_id')),
                     'name': render_value(obj),
                     'data': {
                            'value': value,
                            'printable_value': h.format_number(value),
                            '$area': int(value / 1000),
                            'title': render_value(obj), 
                            'show_title': show_title,
                            'link': dimension_url(obj),
                            '$color': '#333333'
                        }
                     }
            fields.append(field)
        return json.dumps({'children': fields}) 

