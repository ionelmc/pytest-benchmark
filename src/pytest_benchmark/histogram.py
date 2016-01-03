import py

from .utils import TIME_UNITS
from .utils import slugify

try:
    from pygal.graph.box import Box
    from pygal.graph.box import is_list_like
    from pygal.style import DefaultStyle
except ImportError as exc:
    raise ImportError(exc.args, "Please install pygal and pygaljs or pytest-benchmark[histogram]")


class CustomBox(Box):
    def __init__(self, annotations, *args, **kwargs):
        super(CustomBox, self).__init__(*args, **kwargs)
        self.annotations = annotations

    def _box_points(self, serie, _):
        return serie, [serie[0], serie[6]]

    def _format(self, x):
        sup = super(CustomBox, self)._format
        if is_list_like(x):
            return "Min: {0[0]:.4f}\n" \
                   "Q1-1.5IQR: {0[1]:.4f}\n" \
                   "Q1: {0[2]:.4f}\nMedian: {0[3]:.4f}\nQ3: {0[4]:.4f}\n" \
                   "Q3+1.5IQR: {0[5]:.4f}\n" \
                   "Max: {0[6]:.4f}\n\n" \
                   "{0[7]:d} rounds".format(x[:8])
        else:
            return sup(x)

    def _tooltip_data(self, node, value, x, y, classes=None, xlabel=None):
        super(CustomBox, self)._tooltip_data(node, value, x, y, classes=classes, xlabel=None)
        if xlabel in self.annotations:
            self.svg.node(node, 'desc', class_="x_label").text = self.annotations[xlabel]["name"]


def make_plot(benchmarks, title, adjustment):
    class Style(DefaultStyle):
        colors = ["#000000" if row["path"] else DefaultStyle.colors[0]
                  for row in benchmarks]
        font_family = 'Consolas, "Deja Vu Sans Mono", "Bitstream Vera Sans Mono", "Courier New", monospace'

    minimum = int(min(row["min"] * adjustment for row in benchmarks))
    maximum = int(max(
        min(row["max"], row["hd15iqr"]) * adjustment
        for row in benchmarks
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

    plot = CustomBox(
        benchmarks,
        box_mode='tukey',
        x_label_rotation=-90,
        x_labels=[row["source"] for row in benchmarks],
        show_legend=False,
        title=title,
        x_title="Trial",
        y_title="Duration",
        style=Style,
        min_scale=20,
        max_scale=20,
        truncate_label=50,
        range=(minimum, maximum),
        zero=minimum,
        css=[
            "file://style.css",
            "file://graph.css",
            """inline:
                .tooltip .value {
                    font-size: 1em !important;
                }
            """
        ],
        **opts
    )

    for row in benchmarks:
        label = "%s\n%s rounds" % (row["path"], row["rounds"])
        serie = [row[field] * adjustment for field in ["min", "ld15iqr", "q1", "median", "q3", "hd15iqr", "max"]]
        serie.append(row["rounds"])
        plot.add(label, serie)
    return plot


def make_histogram(output_prefix, name, benchmarks, unit, adjustment):
    if name:
        path = "%s-%s.svg" % (output_prefix, slugify(name))
        title = "Speed in %s of %s" % (TIME_UNITS[unit], name),
    else:
        path = "%s.svg" % output_prefix
        title = "Speed in %s" % TIME_UNITS[unit]

    output_file = py.path.local(path).ensure()

    plot = make_plot(
        benchmarks=benchmarks,
        title=title,
        adjustment=adjustment,
    )
    output_file.write_text(plot.render(is_unicode=True), encoding="utf-8")
    return output_file
