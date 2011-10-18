import logging
import pkg_resources
import random

from pylons import config, tmpl_context as c, request
from pylons.i18n import get_lang, _
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool

from genshi.filters import Transformer
from genshi.input import HTML

from openspending import model
from openspending.lib import json
from openspending.ui.lib import helpers as h
from openspending.ui.lib.color import color_range, parent_color
from openspending.plugins.core import SingletonPlugin, implements
from openspending.plugins.interfaces import IMiddleware, IGenshiStreamFilter

log = logging.getLogger(__name__)

TITLE_CUTOFF = 0.02

# TODO: Move CSS to its own file.
HEAD_SNIPPET = """
<!-- OpenSpending Treemap Plugin includes -->
<!--[if IE]><script language="javascript" type="text/javascript" src="/js/excanvas.js"></script><![endif]-->
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
<!-- OpenSpending Treemap Plugin end -->
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

class TreemapPlugin(SingletonPlugin):
    implements(IGenshiStreamFilter, inherit=True)
    implements(IMiddleware, inherit=True)

    def setup_middleware(self, app):
        if not isinstance(app, Cascade):
            log.warn("TreemapMiddleware expected the app to be a Cascade "
                     "object, but it wasn't. Not adding public paths for "
                     "Treemap, so it probably won't work!")
            return app

        max_age = None if asbool(config['debug']) else 3600
        public = pkg_resources.resource_filename(__name__, 'public')

        static_app = StaticURLParser(public, cache_max_age=max_age)

        app.apps.insert(0, static_app)

        return app

    def filter(self, stream):
        if hasattr(c, 'viewstate') and hasattr(c, 'time'):
            vis_height = int(request.params.get('visheight', 400))
            tree_json = self._generate_tree_json(c.viewstate.aggregates,
                c.dataset.name, c.time, c.viewstate.totals.get(c.time, 0))
            ts_json = self._generate_ts_json(c.viewstate.aggregates, 
                c.dataset.name, c.times)
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

    def _generate_tree_json(self, aggregates, dataset, time, total):
        fields = []
        for obj, time_values in aggregates:
            value = time_values.get(time)
            if value <= 0:
                continue
            color = self._get_color(obj, aggregates, time_values)
            show_title = (value/max(1,total)) > TITLE_CUTOFF
            link = h.classifier_url(dataset, obj) if \
                    isinstance(obj, dict) else ''

            # Maybe we're at a leaf node. In which case, see if this view
            # corresponds to a single entry, and if so, link to that.
            #if link == '#':
            #    curs = model.entry.find({c.view.drilldown: obj})
            #    if curs.count() == 1:
            #        e = model.entry.get_ref_dict(curs[0])
            #        link = h.dimension_url(e)

            field = {'children': [],
                     'id': str(obj.get('_id')) if isinstance(obj, dict) else hash(obj),
                     'name': h.render_value(obj),
                     'data': {
                            'value': value,
                            'printable_value': h.format_number(value),
                            '$area': int(value / 1000),
                            'title': h.render_value(obj),
                            'show_title': show_title,
                            'link': link,
                            '$color': color
                        }
                     }
            fields.append(field)
        if not len(fields):
            return None
        return json.dumps({'children': fields})

    def _generate_ts_json(self, aggregates, dataset, times):
        to_id = lambda obj: str(obj.get('id')) if isinstance(obj, dict) else hash(obj)
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
                    'title': h.render_value(obj),
                    'link': h.classifier_url(dataset, obj) if \
                            isinstance(obj, dict) else None,
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

