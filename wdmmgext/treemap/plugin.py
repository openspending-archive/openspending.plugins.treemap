try:
    import json 
except ImportError:
    import simplejson as json
import random

from pylons.i18n import get_lang, _
from genshi.filters import Transformer
from genshi.input import HTML

from wdmmg.lib import helpers as h
from wdmmg.lib.color import color_range, parent_color
from wdmmg.plugins import SingletonPlugin, implements
from wdmmg.plugins import IGenshiStreamFilter 

TITLE_CUTOFF = 0.02

# TODO: Move CSS to its own file. 
HEAD_SNIPPET = """
<!-- wdmmg-treemap includes -->
<script src="/js/thejit-2.js"></script>
<script src="/js/jitload.js"></script>
<script>
$(document).ready(function() {
    OpenSpending.DatasetPage.init({
        treemapData: %s,
        timeseriesData: %s
    });
});
</script>
<style>
#mainvis {
	position: relative;
	overflow: hidden;
    cursor: pointer;
	color: #fff;
	font-size: 0.8em;
	font-weight: bold; 
}

#mainvis div.desc {
    padding: 0.8em;
	font-weight: normal;
    overflow: hidden; 
}

#mainvis h2 {
    font-family: Graublau, Georgia, serif; 
	font-size: 1.6em;
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

VIS_SELECT_SNIPPET = """
    <select id="_vis_select"> 
        <option value="treemap">Composition</option>
        <option value="timeseries">Time Series</option>
    </select>
"""

BODY_SNIPPET = """
<div id='mainvis' style='width: auto; height: %spx;'>&nbsp;</div><br/>
"""

class TreemapGenshiStreamFilter(SingletonPlugin):
    implements(IGenshiStreamFilter, inherit=True)

    def filter(self, stream):
        from pylons import tmpl_context as c, request
        if hasattr(c, 'viewstate') and hasattr(c, 'time'):
            vis_height = int(request.params.get('visheight', 400))
            tree_json = self._generate_tree_json(c.viewstate.aggregates, 
                c.time, c.viewstate.totals.get(c.time, 0))
            ts_json = self._generate_ts_json(c.viewstate.aggregates, c.times)
            if tree_json is not None:
                stream = stream | Transformer('//form[@id="_time_form"]')\
                   .prepend(HTML(VIS_SELECT_SNIPPET))
                stream = stream | Transformer('html/head')\
                   .append(HTML(HEAD_SNIPPET % (tree_json, ts_json)))
                stream = stream | Transformer('//div[@id="vis"]')\
                    .append(HTML(BODY_SNIPPET % vis_height))
        return stream

    def _get_color(self, obj, aggregates, time_values):
        if isinstance(obj, dict):
            pcolor = parent_color(obj)
            crange = list(color_range(pcolor, len(aggregates)))
            return list(crange)[aggregates.index((obj, time_values))]
        else:
            return '#333333'

    def _generate_tree_json(self, aggregates, time, total):
        from wdmmg.lib.helpers import dimension_url, render_value
        fields = []
        for obj, time_values in aggregates:
            value = time_values.get(time)
            if value <= 0: 
                continue
            color = self._get_color(obj, aggregates, time_values)
            show_title = (value/max(1,total)) > TITLE_CUTOFF
            field = {'children': [],
                     'id': str(obj.get('_id')) if isinstance(obj, dict) else hash(obj),
                     'name': render_value(obj),
                     'data': {
                            'value': value,
                            'printable_value': h.format_number(value),
                            '$area': int(value / 1000),
                            'title': render_value(obj), 
                            'show_title': show_title,
                            'link': dimension_url(obj),
                            '$color': color
                        }
                     }
            fields.append(field)
        if not len(fields):
            return None
        return json.dumps({'children': fields}) 

    def _generate_ts_json(self, aggregates, times):
        from wdmmg.lib.helpers import dimension_url, render_value
        to_id = lambda obj: str(obj.get('_id')) if isinstance(obj, dict) else hash(obj)
        label = [to_id(o) for o, tv in aggregates]
        values = []
        colored = False
        colors = []
        for time in times:
            _values = []
            for obj, time_values in aggregates:
                if not colored:
                    colors.append(self._get_color(obj, aggregates, time_values))
                _values.append(time_values.get(time, 0))
            values.append({"label": str(time), "values": _values})
            colored = True
        details = {}
        for obj, ts in aggregates:
            props = {
                    'title': render_value(obj),
                    'link': dimension_url(obj),
                    }
            details[to_id(obj)] = props
        if not len(values):
            return None
        return json.dumps({
            'label': label,
            'details': details,
            'values': values,
            'colors': colors
            })
