from pytest_benchmark.utils import time_unit

try:
    from pygal.graph.box import Box
    from pygal.graph.box import is_list_like
    from pygal.style import DefaultStyle
except ImportError as exc:
    raise ImportError(exc.args, "Please install pygal and pygaljs or pytest-benchmark[histogram]")


class Plot(Box):
    def __init__(self, annotations, *args, **kwargs):
        super(Plot, self).__init__(*args, **kwargs)
        self.annotations = annotations

    def _box_points(self, serie, _):
        return (None,
                serie[0],
                serie[1],
                serie[2],
                serie[3],
                serie[4],
                serie[5]), []

    def _format(self, x):
        sup = super(Box, self)._format
        if is_list_like(x):
            return 'Min: %s\nQ1: %s\nMedian: %s\nQ3: %s\nMax: %s\nRounds: %s' % tuple(map(sup, x[1:]))
        else:
            return sup(x)

    def _tooltip_data(self, node, value, x, y, classes=None, xlabel=None):
        super(Plot, self)._tooltip_data(node, value, x, y, classes=classes, xlabel=None)
        if xlabel in self.annotations:
            self.svg.node(node, 'desc', class_="x_label").text = self.annotations[xlabel]['name']


def make_plot(bench_name, table, compare, current, annotations, sort):
    class Style(DefaultStyle):
        colors = []
        font_family = 'Consolas, "Deja Vu Sans Mono", "Bitstream Vera Sans Mono", "Courier New", monospace'

        for label, row in table:
            if label == current:
                colors.append(DefaultStyle.colors[0])
            elif compare and str(compare.basename).startswith(label):
                colors.append(DefaultStyle.colors[2])
            else:
                colors.append('#000000')

    unit, adjustment = time_unit(min(
        row[sort]
        for _, row in table
    ))

    minimum = int(min(row['min'] * adjustment for _, row in table))
    maximum = int(max(row['max'] * adjustment for _, row in table) + 1)

    try:
        import pygaljs
    except ImportError:
        opts = {}
    else:
        opts = {
            "js": [
                pygaljs.uri("2.0.x", "pygal-tooltips.js")
            ]
        }

    plot = Plot(
        annotations,
        x_label_rotation=-90,
        x_labels=[label for label, _ in table],
        show_legend=False,
        title="Speed in %sseconds of %s" % (unit, bench_name),
        x_title="Trial",
        y_title="%ss" % unit,
        style=Style,
        min_scale=20,
        max_scale=20,
        range=(minimum, maximum),
        zero=minimum,
        css=[
            "file://style.css",
            "file://graph.css",
            "inline:.axis.x text {text-anchor: middle !important}"
        ],
        **opts
    )

    for label, row in table:
        if label in annotations:
            label += '\n@' + annotations[label]['datetime']
        serie = [row[field] * adjustment for field in ['min', 'q1', 'median', 'q3', 'max']]
        serie.append(row['rounds'])
        plot.add(label, serie)
    return plot
