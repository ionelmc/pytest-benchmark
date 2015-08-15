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
        return serie, [serie[0], serie[6]]

    def _format(self, x):
        sup = super(Box, self)._format
        if is_list_like(x):
            return "Min: {0[0]:.4f}\n" \
                   "Q1-1.5IQR: {0[1]:.4f}\n" \
                   "Q1: {0[2]:.4f}\nMedian: {0[3]:.4f}\nQ3: {0[4]:.4f}\n" \
                   "Q3+1.5IQR: {0[5]:.4f}\n" \
                   "Max: {0[6]:.4f}".format(x[:7])
        else:
            return sup(x)

    def _tooltip_data(self, node, value, x, y, classes=None, xlabel=None):
        super(Plot, self)._tooltip_data(node, value, x, y, classes=classes, xlabel=None)
        if xlabel in self.annotations:
            self.svg.node(node, 'desc', class_="x_label").text = self.annotations[xlabel]["name"]


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
                colors.append("#000000")

    unit, adjustment = time_unit(min(
        row[sort]
        for _, row in table
    ))

    minimum = int(min(row["min"] * adjustment for _, row in table))
    maximum = int(max(
        min(row["max"], row["hd15iqr"]) * adjustment
        for _, row in table
    ) + 1)

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
        box_mode='tukey',
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
            """inline:
                .axis.x text {
                    text-anchor: middle !important;
                }
                .tooltip .value {
                    font-size: 1em !important;
                }
            """
        ],
        **opts
    )

    for label, row in table:
        if label in annotations:
            label += "\n@%s - %s rounds" % (annotations[label]["datetime"], row["rounds"])
        serie = [row[field] * adjustment for field in ["min", "ld15iqr", "q1", "median", "q3", "hd15iqr", "max"]]
        plot.add(label, serie)
    return plot
