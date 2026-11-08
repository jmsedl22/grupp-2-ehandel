import warnings
from copy import deepcopy
from textwrap import fill
from typing import Any
from unittest.mock import Mock, patch

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.patches import PathPatch, Rectangle

from src import metrics, viz
from src.ecommerce import CommerceAnalyzer

matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def plotting_environment(monkeypatch):
    monkeypatch.setattr(plt, "show", Mock())
    with plt.ioff():
        try:
            yield
        finally:
            plt.close("all")


@pytest.fixture
def settings():
    return {
        "figure_size": (7.0, 4.0),
        "background_color": "#FFFFFF",
        "text_color": "#243239",
        "grid_color": "#D9E2E3",
        "main_color": "#246B75",
        "histogram_color": "#72A9AB",
        "aov_color": "#B85B31",
        "median_color": "#20434B",
        "font_family": "DejaVu Sans",
        "font_size": 9,
        "title_size": 12,
    }


@pytest.mark.parametrize("interactive", [False, True])
def test_chart_restores_settings_and_interactive_mode(settings, interactive):
    with plt.ion() if interactive else plt.ioff():
        before = matplotlib.rcParams.copy()
        figures_before = plt.get_fignums()

        with viz._chart(settings) as (fig, ax):
            assert not plt.isinteractive()
            assert tuple(fig.get_size_inches()) == pytest.approx(
                settings["figure_size"]
            )
            assert ax.get_facecolor() == to_rgba(settings["background_color"])
            assert matplotlib.rcParams["font.size"] == settings["font_size"]

        assert plt.isinteractive() == interactive
        assert matplotlib.rcParams == before
        assert plt.get_fignums() == figures_before
        fig.canvas.draw()


def test_chart_closes_figure_and_restores_settings_after_exception(settings):
    before = matplotlib.rcParams.copy()
    figures_before = plt.get_fignums()
    interactive_before = plt.isinteractive()

    with (
        pytest.raises(RuntimeError, match="intentional"),
        viz._chart(settings),
    ):
        raise RuntimeError("intentional chart failure")

    assert matplotlib.rcParams == before
    assert plt.get_fignums() == figures_before
    assert plt.isinteractive() == interactive_before


def test_city_chart_preserves_missing_labels_and_input(settings):
    summary = metrics.city_summary(pd.DataFrame({
        "city": ["A", None],
        "revenue": [100.0, 50.0],
    }))
    original = summary.copy(deep=True)
    figures_before = plt.get_fignums()

    fig = viz.plot_revenue_city(summary, settings)
    fig.canvas.draw()
    ax = fig.axes[0]

    assert isinstance(fig, Figure)
    assert [tick.get_text() for tick in ax.get_yticklabels()] == [
        "A", "Ej angivet",
    ]
    widths = []
    for bar in ax.patches:
        assert isinstance(bar, Rectangle)
        widths.append(bar.get_width())
    assert widths == [100.0, 50.0]
    assert all(
        bar.get_facecolor() == to_rgba(settings["main_color"])
        for bar in ax.patches
    )
    assert plt.get_fignums() == figures_before
    pd.testing.assert_frame_equal(summary, original)


@pytest.mark.parametrize("category_empty, city_empty", [
    (False, False), (True, True), (True, False), (False, True),
])
def test_combined_revenue_chart_preserves_prepared_panels(
    settings, category_empty, city_empty,
):
    category = pd.DataFrame({
        "category": [None, np.nan, pd.NA,
                     "En mycket lång kategori med flera ord som måste radbrytas",
                     "EttOvanligtLångtSammanhängandeKategorinamnSomRadbryts"],
        "revenue": [10.0, 1250.5, 0.0, 4.0, 2.0],
        "share_pct": [np.nan, 50.0, 0.0, pd.NA, None],
        "original_category": ["original"] * 5,
        "order_count": [1, 2, 3, 4, 5],
    }, index=[9, 3, 7, 1, 5])
    city = pd.DataFrame({
        "city": ["B", "A"], "revenue": [20.0, 2000.0],
        "share_pct": [1.0, 99.0], "original_city": ["B", "A"],
    }, index=[8, 2])
    if category_empty:
        category = category.iloc[:0].copy()
    if city_empty:
        city = city.iloc[:0].copy()
    originals = [category.copy(deep=True), city.copy(deep=True)]
    settings_before = deepcopy(settings)
    figures_before = plt.get_fignums()
    rc_before = matplotlib.rcParams.copy()
    interactive_before = plt.isinteractive()

    fig = viz.plot_revenue_category_city(category, city, settings)
    fig.canvas.draw()

    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2
    top, bottom = fig.axes
    assert top.get_shared_x_axes().joined(top, bottom)
    assert top.get_xlim() == pytest.approx(bottom.get_xlim())
    assert top.xaxis.get_major_formatter() is bottom.xaxis.get_major_formatter()
    if not (category_empty and city_empty):
        for ax in fig.axes:
            assert ax.xaxis.get_major_formatter()(1234.5, 0) == "1 234,50"
    heights = []
    for ax, summary, column, title, ylabel, original in zip(
        fig.axes, [category, city], ["category", "city"],
        ["Intäkt per kategori", "Intäkt per stad"], ["Kategori", "Stad"],
        originals, strict=True,
    ):
        labels = [
            fill("Ej angivet" if pd.isna(value) else str(value), width=24)
            for value in summary[column]
        ]
        heights.append(max(
            settings["figure_size"][1],
            1.8 + 0.4 * sum(label.count("\n") + 1 for label in labels),
        ))
        assert ax.get_title() == title
        assert ax.get_ylabel() == ylabel
        assert ax.get_xlabel() == "Intäkt [SEK]"
        margins = ax.margins()
        assert margins is not None
        assert margins[0] == pytest.approx(0.4)
        widths = []
        for bar in ax.patches:
            assert isinstance(bar, Rectangle)
            widths.append(bar.get_width())
            assert bar.get_facecolor() == to_rgba(settings["main_color"])
        np.testing.assert_allclose(
            np.asarray(widths, dtype=float),
            np.asarray(summary["revenue"], dtype=float),
        )
        if summary.empty:
            assert not ax.axison
            assert [text.get_text() for text in ax.texts] == ["Inga data"]
        else:
            assert ax.yaxis_inverted()
            assert [tick.get_text() for tick in ax.get_yticklabels()] == labels
            assert any(line.get_visible() for line in ax.get_xgridlines())
            assert not any(line.get_visible() for line in ax.get_ygridlines())
            expected = [] if column == "city" else [
                "10,00 SEK (—)", "1 250,50 SEK (50,00 %)",
                "0,00 SEK (0,00 %)", "4,00 SEK (—)", "2,00 SEK (—)",
            ]
            assert [text.get_text() for text in ax.texts] == expected
        pd.testing.assert_frame_equal(summary, original)
    assert tuple(fig.get_size_inches()) == pytest.approx((
        settings["figure_size"][0], sum(heights),
    ))
    subplotspec = top.get_subplotspec()
    assert subplotspec is not None
    np.testing.assert_allclose(
        np.asarray(subplotspec.get_gridspec().get_height_ratios(), dtype=float),
        heights,
    )
    if city_empty and not category_empty:
        assert top.get_xticklabels()
        assert all(tick.get_visible() for tick in top.get_xticklabels())
        assert any(tick.get_text() for tick in top.get_xticklabels())
    assert settings == settings_before
    assert plt.get_fignums() == figures_before
    assert matplotlib.rcParams == rc_before
    assert plt.isinteractive() == interactive_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("column", ["category", "city"])
@pytest.mark.parametrize("minimum_height", [4.0, 12.0])
@pytest.mark.parametrize("zero_total", [False, True])
def test_standalone_revenue_bars_wrap_size_and_annotate(
    settings, column, minimum_height, zero_total,
):
    settings = {**settings, "figure_size": (7.0, minimum_height)}
    summary = pd.DataFrame({
        column: [None, "En mycket lång ursprunglig etikett med många ord " * 4],
        "revenue": [0.0, 0.0] if zero_total else [12.5, 1250.0],
        "share_pct": [np.nan, pd.NA] if zero_total else [np.nan, 99.0],
        f"original_{column}": ["missing", "original long label"],
        "order_count": [3, 4],
    }, index=[7, 2])
    original = summary.copy(deep=True)
    settings_before = deepcopy(settings)
    labels = ["Ej angivet", fill(summary[column].iloc[1], width=24)]
    figures_before = plt.get_fignums()

    if column == "category":
        fig = viz.plot_revenue_category(
            summary, settings, pd.Timestamp("2024-01-02"), pd.Timestamp("2024-03-04"),
        )
    else:
        fig = viz.plot_revenue_city(summary, settings)
    fig.canvas.draw()
    ax = fig.axes[0]

    assert [tick.get_text() for tick in ax.get_yticklabels()] == labels
    assert tuple(fig.get_size_inches()) == pytest.approx((
        7.0, max(minimum_height, 1.8 + 0.4 * sum(
            label.count("\n") + 1 for label in labels
        )),
    ))
    if column == "category":
        assert ax.get_title() == "Intäkt per kategori\n2024-01-02 – 2024-03-04"
        assert ax.get_xlabel() == "Intäkt"
        assert ax.get_ylabel() == "Kategori"
        margins = ax.margins()
        assert margins is not None
        assert margins[0] == pytest.approx(0.4)
        assert [text.get_text() for text in ax.texts] == (
            ["0,00 SEK (—)", "0,00 SEK (—)"] if zero_total else
            ["12,50 SEK (—)", "1 250,00 SEK (99,00 %)"]
        )
    else:
        assert ax.get_title() == "Intäkt per stad"
        assert ax.get_xlabel() == "Intäkt [SEK]"
        assert ax.get_ylabel() == "Stad"
        assert not ax.texts
    pd.testing.assert_frame_equal(summary, original)
    assert settings == settings_before
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("empty", [False, True])
def test_analyzer_combined_revenue_forwards_summaries(settings, monkeypatch, empty):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = pd.DataFrame({
        "category": ["B", None, "A"], "city": [None, "X", "X"],
        "revenue": [5.0, 10.0, 20.0], "order_id": ["A", "A", "B"],
    })
    if empty:
        analyzer.dataframe = analyzer.dataframe.iloc[:0].copy()
    analyzer.settings = settings
    original = analyzer.dataframe.copy(deep=True)
    settings_before = deepcopy(settings)
    expected = [metrics.category_summary(original), metrics.city_summary(original)]
    prepare = [Mock(wraps=metrics.category_summary), Mock(wraps=metrics.city_summary)]
    monkeypatch.setattr(metrics, "category_summary", prepare[0])
    monkeypatch.setattr(metrics, "city_summary", prepare[1])
    render = Mock(wraps=viz.plot_revenue_category_city)
    monkeypatch.setattr(viz, "plot_revenue_category_city", render)

    fig = analyzer.plot_revenue_category_city()
    fig.canvas.draw()

    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2
    render.assert_called_once()
    assert render.call_args.args[2] is settings
    for spy, supplied, summary in zip(prepare, render.call_args.args[:2], expected):
        spy.assert_called_once()
        assert spy.call_args.args[0] is analyzer.dataframe
        pd.testing.assert_frame_equal(supplied, summary)
    pd.testing.assert_frame_equal(analyzer.dataframe, original)
    assert settings == settings_before


@pytest.mark.parametrize("plotter, columns", [
    (viz.plot_revenue_city, ["city", "revenue", "share_pct"]),
    (viz.plot_monthly_revenue, [
        "month", "revenue", "order_count", "calendar_days", "observed_days",
        "coverage_status", "revenue_per_day", "aov",
    ]),
])
def test_prepared_charts_handle_empty_input(settings, plotter, columns):
    summary = pd.DataFrame(columns=columns)

    fig = plotter(summary, settings)
    fig.canvas.draw()
    ax = fig.axes[0]

    assert not ax.axison
    assert [text.get_text() for text in ax.texts] == ["Inga data"]
    assert ax.get_legend() is None
    assert plt.get_fignums() == []


def test_monthly_chart_preserves_overall_totals_dates_gaps_and_zero(settings):
    source = pd.DataFrame({
        "date": pd.to_datetime([
            "2024-03-01", "2024-01-10", "2024-03-15", "2024-01-20",
        ]),
        "order_id": ["A", "B", "C", "D"],
        "category": ["Books", "Books", "Clothing", None],
        "revenue": [10.0, 5.0, 20.0, -5.0],
    })
    summary = metrics.monthly_summary(source)
    original = summary.copy(deep=True)
    figures_before = plt.get_fignums()

    fig = viz.plot_monthly_revenue(summary, settings)
    fig.canvas.draw()
    ax = fig.axes[0]

    assert len(ax.lines) == 1
    line = ax.lines[0]
    assert pd.to_datetime(np.asarray(line.get_xdata())).tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    np.testing.assert_allclose(
        np.asarray(line.get_ydata(), dtype=float),
        [0.0, np.nan, 30.0],
        equal_nan=True,
    )
    assert [tick.get_text() for tick in ax.get_xticklabels()] == [
        "januari\n2024", "februari\n2024", "mars\n2024",
    ]
    assert to_rgba(line.get_color()) == to_rgba(settings["main_color"])
    assert ax.get_title() == "Observerade intäkter per månad"
    assert ax.get_ylabel() == "Observerade intäkter [SEK]"
    assert "månader utan observationer" in ax.get_xlabel()
    assert ax.get_legend() is None
    assert plt.get_fignums() == figures_before
    pd.testing.assert_frame_equal(summary, original)


def test_analyzer_monthly_chart_uses_overall_monthly_summary(settings):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-03-01"]),
        "order_id": ["A", "B", "C"],
        "category": ["Books", "Clothing", None],
        "revenue": [4.0, 6.0, 30.0],
    })
    analyzer.settings = settings
    original = analyzer.dataframe.copy(deep=True)

    fig = analyzer.plot_monthly_revenue()
    fig.canvas.draw()

    assert isinstance(fig, Figure)
    assert len(fig.axes[0].lines) == 1
    np.testing.assert_allclose(
        np.asarray(fig.axes[0].lines[0].get_ydata(), dtype=float),
        [10.0, np.nan, 30.0],
        equal_nan=True,
    )
    pd.testing.assert_frame_equal(analyzer.dataframe, original)


@pytest.mark.parametrize("value, expected", [
    ("2024-01-15", "januari 2024"),
    ("2024-09-01", "september 2024"),
    ("2024-12-31", "december 2024"),
    (pd.NaT, "—"),
])
def test_format_month_uses_swedish_names_and_handles_missing(value, expected):
    assert viz._format_month(value) == expected


@pytest.mark.parametrize("month_count", [1, 12])
def test_monthly_chart_scales_width_and_pads_date_limits(settings, month_count):
    source = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=month_count, freq="MS"),
        "order_id": list(range(month_count)),
        "revenue": [10.0] * month_count,
    })
    summary = metrics.monthly_summary(source)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = viz.plot_monthly_revenue(summary, settings)
        fig.canvas.draw()

    ax = fig.axes[0]
    assert tuple(fig.get_size_inches()) == pytest.approx((
        max(settings["figure_size"][0], 1.5 + 0.9 * month_count),
        settings["figure_size"][1],
    ))
    positions = np.asarray(ax.lines[0].get_xdata(orig=False), dtype=float)
    np.testing.assert_allclose(np.asarray(ax.get_xticks()), positions)
    assert ax.get_xlim() == pytest.approx((positions[0] - 15, positions[-1] + 15))


@pytest.mark.parametrize("edges, counts", [
    ([], []),
    ([0.0, 10.0, 20.0], [0, 0]),
    ([0.0, 10.0, 30.0], [2, 1]),
])
def test_order_distribution_handles_empty_zero_and_nonempty(settings, edges, counts):
    histogram = {"bin_edges": edges, "counts": counts}
    summary = {
        "aov": 9.0 if counts else 0.0,
        "median_revenue": 5.0 if counts else float("nan"),
    }
    original_histogram = deepcopy(histogram)
    original_summary = summary.copy()
    figures_before = plt.get_fignums()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = viz.plot_order_value_distribution(histogram, summary, settings)
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert len(ax.patches) == len(counts)
    for index, bar in enumerate(ax.patches):
        assert isinstance(bar, Rectangle)
        assert bar.get_x() == pytest.approx(edges[index])
        assert bar.get_width() == pytest.approx(edges[index + 1] - edges[index])
        assert bar.get_height() == counts[index]
        assert bar.get_facecolor() == to_rgba(settings["histogram_color"])
        assert bar.get_edgecolor() == to_rgba(settings["background_color"])

    if counts:
        assert ax.get_ylim()[1] > 0
        assert len(ax.lines) == 2
        aov_line, median_line = ax.lines
        np.testing.assert_allclose(
            np.asarray(aov_line.get_xdata(), dtype=float), [9.0, 9.0],
        )
        np.testing.assert_allclose(
            np.asarray(median_line.get_xdata(), dtype=float), [5.0, 5.0],
        )
        assert aov_line.get_linestyle() == "--"
        assert median_line.get_linestyle() == "-"
        assert to_rgba(aov_line.get_color()) == to_rgba(settings["aov_color"])
        assert to_rgba(median_line.get_color()) == to_rgba(settings["median_color"])
        assert aov_line.get_zorder() > median_line.get_zorder()
        legend = ax.get_legend()
        assert legend is not None
        assert [text.get_text() for text in legend.get_texts()] == [
            "AOV: 9,00 SEK", "Median: 5,00 SEK",
        ]
        assert ax.xaxis.get_major_formatter()(1234.5, 0) == "1 234,50"
        assert ax.yaxis.get_major_formatter()(1000, 0) == "1 000"
        ticks = np.asarray(ax.get_yticks(), dtype=float)
        np.testing.assert_allclose(ticks, np.round(ticks))
    else:
        assert not ax.axison
        assert [text.get_text() for text in ax.texts] == ["Inga data"]
        assert len(ax.lines) == 0
        assert ax.get_legend() is None

    assert plt.get_fignums() == figures_before
    assert histogram == original_histogram
    pd.testing.assert_series_equal(pd.Series(summary), pd.Series(original_summary))


@pytest.mark.parametrize("revenue", [0.0, 7.0, -10.0])
def test_order_distribution_handles_constant_order_totals(settings, revenue):
    source = pd.DataFrame({
        "order_id": ["A", "A", "B"],
        "revenue": [revenue / 2, revenue / 2, revenue],
    })
    histogram = metrics.order_histogram(source)
    summary = metrics.order_summary(source)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = viz.plot_order_value_distribution(histogram, summary, settings)
        fig.canvas.draw()

    ax = fig.axes[0]
    assert len(ax.patches) == 25
    heights = []
    for bar in ax.patches:
        assert isinstance(bar, Rectangle)
        assert bar.get_width() > 0
        heights.append(bar.get_height())
    assert sum(heights) == 2
    assert len(ax.lines) == 2
    for line in ax.lines:
        np.testing.assert_allclose(
            np.asarray(line.get_xdata(), dtype=float), [revenue, revenue],
        )
    assert ax.get_ylim()[1] > 0
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 2


@pytest.mark.parametrize("empty", [False, True])
def test_analyzer_order_distribution_uses_combined_orders(settings, empty):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = pd.DataFrame({
        "order_id": ["A", "A", "B", "C"],
        "revenue": [10.0, 20.0, 50.0, 100.0],
    })
    if empty:
        analyzer.dataframe = analyzer.dataframe.iloc[:0].copy()
    analyzer.settings = settings
    original = analyzer.dataframe.copy(deep=True)
    figures_before = plt.get_fignums()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = analyzer.plot_order_value_distribution()
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    if empty:
        assert not ax.axison
        assert len(ax.patches) == 0
        assert len(ax.lines) == 0
    else:
        assert len(ax.patches) == 25
        heights = []
        for bar in ax.patches:
            assert isinstance(bar, Rectangle)
            heights.append(bar.get_height())
        assert sum(heights) == 3
        assert len(ax.lines) == 2
        np.testing.assert_allclose(
            np.asarray(ax.lines[0].get_xdata(), dtype=float), [60.0, 60.0],
        )
        np.testing.assert_allclose(
            np.asarray(ax.lines[1].get_xdata(), dtype=float), [50.0, 50.0],
        )
    assert plt.get_fignums() == figures_before
    pd.testing.assert_frame_equal(analyzer.dataframe, original)


@pytest.fixture
def typical_order_source():
    return pd.DataFrame({
        "order_id": ["A", "A", "B", "C"],
        "revenue": [40.0, 60.0, 200.0, 900.0],
        "units": [1, 2, 1, 5],
    })


@pytest.mark.parametrize("case", ["valid", "prepared", "empty", "empty_units"])
def test_typical_order_uses_prepared_panels(settings, typical_order_source, case):
    source = typical_order_source.iloc[:0] if case == "empty" else typical_order_source
    orders, unit_counts = metrics.calculate_typical_order_data(source)
    histogram = metrics.order_histogram(source)
    if case == "prepared":
        # Different metadata per row and no index 0 expose recomputation/label lookup.
        columns = ["average_revenue", "median_revenue", "median_units", "average_units"]
        orders[columns] = -999.0
        orders.loc[orders.index[0], columns] = [1234.5, 175.0, 2.25, 4.75]
        orders.index = [7, 2, 9]
    if case == "empty_units":
        unit_counts = unit_counts.iloc[:0].copy()
    originals = [orders.copy(deep=True), unit_counts.copy(deep=True)]
    histogram_before, settings_before = deepcopy(histogram), deepcopy(settings)
    rc_before, figures_before = matplotlib.rcParams.copy(), plt.get_fignums()
    interactive_before = plt.isinteractive()

    with (
        plt.ion(),
        patch.object(viz, "_draw_order_histogram", wraps=viz._draw_order_histogram) as draw,
        patch.object(Axes, "hist", side_effect=AssertionError("Use prepared histogram")),
        patch.object(Figure, "tight_layout", side_effect=AssertionError("Use _chart")),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("error")
        fig = viz.plot_typical_order(orders, unit_counts, histogram, settings)
        fig.canvas.draw()
        assert plt.isinteractive()

    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2
    assert tuple(fig.get_size_inches()) == pytest.approx((14.0, 4.0))
    assert [text.get_text() for text in fig.texts] == ["HUR SER EN TYPISK ORDER UT?"]
    left, right = fig.axes
    spec = left.get_subplotspec()
    assert spec is not None
    assert spec.get_gridspec().ncols == 2
    for ax in fig.axes:
        assert ax.get_facecolor() == to_rgba(settings["background_color"])
        if case == "empty" or (ax is right and case == "empty_units"):
            assert not ax.axison
            assert [text.get_text() for text in ax.texts] == ["Inga data"]
            assert len(ax.patches) == len(ax.lines) == 0
            assert ax.get_legend() is None
    if case == "empty":
        draw.assert_not_called()
    else:
        aov, median = (1234.5, 175.0) if case == "prepared" else (400.0, 200.0)
        draw.assert_called_once()
        supplied_ax, supplied_histogram, summary, supplied_settings = draw.call_args.args
        assert supplied_ax is left and supplied_histogram is histogram
        assert supplied_settings is settings
        assert summary == {"aov": aov, "median_revenue": median}
        assert left.get_title() == "FÖRDELNING AV ORDERVÄRDE"
        assert left.get_xlabel() == "Ordervärde [SEK]"
        assert left.get_ylabel() == "Antal order"
        assert len(left.patches) == len(histogram["counts"])
        assert sum(histogram["counts"]) == 3
        for bar, start, end, count in zip(
            left.patches, histogram["bin_edges"][:-1],
            histogram["bin_edges"][1:], histogram["counts"], strict=True,
        ):
            assert isinstance(bar, Rectangle)
            assert bar.get_x() == pytest.approx(start)
            assert bar.get_width() == pytest.approx(end - start)
            assert bar.get_height() == count
            assert bar.get_facecolor() == to_rgba(settings["histogram_color"])
            assert bar.get_edgecolor() == to_rgba(settings["background_color"])
        assert len(left.lines) == 2
        for line, value in zip(left.lines, [aov, median], strict=True):
            np.testing.assert_allclose(
                np.asarray(line.get_xdata(), dtype=float), [value, value],
            )
        assert right.get_title() == "ANTAL PRODUKTER PER ORDER"
        assert right.get_xlabel() == "Antal produkter"
        assert right.get_ylabel() == "Antal order"
        if case != "empty_units":
            assert len(right.patches) == 3
            for bar, quantity in zip(right.patches, [1, 3, 5], strict=True):
                assert isinstance(bar, Rectangle)
                assert bar.get_x() + bar.get_width() / 2 == pytest.approx(quantity)
                assert bar.get_height() == 1
                assert bar.get_facecolor() == to_rgba(settings["main_color"])
                assert bar.get_edgecolor() == to_rgba(settings["background_color"])
            assert len(right.lines) == 2
            values = [2.25, 4.75] if case == "prepared" else [3.0, 3.0]
            for line, value, style, color, zorder in zip(
                right.lines, values, ["-", "--"], ["median_color", "aov_color"],
                [3, 4], strict=True,
            ):
                np.testing.assert_allclose(
                    np.asarray(line.get_xdata(), dtype=float), [value, value],
                )
                assert line.get_linestyle() == style
                assert line.get_linewidth() == 2
                assert line.get_zorder() == zorder
                assert to_rgba(line.get_color()) == to_rgba(settings[color])
            legend = right.get_legend()
            assert legend is not None
            assert [text.get_text() for text in legend.get_texts()] == (
                ["Median: 2,25", "Medelvärde: 4,75"] if case == "prepared" else
                ["Median: 3,00", "Medelvärde: 3,00"]
            )
            np.testing.assert_allclose(
                np.asarray(right.get_xticks(), dtype=float), [1, 3, 5],
            )
            for axis in (right.xaxis, right.yaxis):
                assert axis.get_major_formatter()(1234, 0) == "1 234"
            ticks = np.asarray(right.get_yticks(), dtype=float)
            np.testing.assert_allclose(ticks, np.round(ticks))
            assert right.get_ylim()[0] == 0 < right.get_ylim()[1]
            assert any(line.get_visible() for line in right.get_ygridlines())
            assert not any(line.get_visible() for line in right.get_xgridlines())
    for actual, original in zip([orders, unit_counts], originals, strict=True):
        pd.testing.assert_frame_equal(actual, original)
    assert histogram == histogram_before and settings == settings_before
    assert matplotlib.rcParams == rc_before
    assert plt.isinteractive() == interactive_before
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("empty", [False, True])
def test_analyzer_typical_order_forwards_prepared_data(
    settings, typical_order_source, empty,
):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = (
        typical_order_source.iloc[:0].copy() if empty else typical_order_source
    )
    analyzer.settings = settings
    original, settings_before = analyzer.dataframe.copy(deep=True), deepcopy(settings)
    expected_orders, expected_units = metrics.calculate_typical_order_data(original)
    expected_histogram = metrics.order_histogram(original)
    rc_before, figures_before = matplotlib.rcParams.copy(), plt.get_fignums()
    interactive_before = plt.isinteractive()

    with (
        patch.object(
            metrics, "calculate_typical_order_data",
            wraps=metrics.calculate_typical_order_data,
        ) as prepare,
        patch.object(metrics, "order_histogram", wraps=metrics.order_histogram) as histogram,
        patch.object(viz, "plot_typical_order", wraps=viz.plot_typical_order) as render,
        patch.object(Axes, "hist", side_effect=AssertionError("Use prepared histogram")),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("error")
        fig = analyzer.plot_typical_order()
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    render.assert_called_once()
    for spy in (prepare, histogram):
        spy.assert_called_once()
        assert spy.call_args.args[0] is analyzer.dataframe
    supplied_orders, supplied_units, supplied_histogram, supplied_settings = (
        render.call_args.args
    )
    pd.testing.assert_frame_equal(supplied_orders, expected_orders)
    pd.testing.assert_frame_equal(supplied_units, expected_units)
    assert supplied_histogram == expected_histogram
    assert supplied_settings is settings
    assert len(fig.axes) == 2
    if empty:
        for ax in fig.axes:
            assert not ax.axison
            assert [text.get_text() for text in ax.texts] == ["Inga data"]
            assert len(ax.patches) == len(ax.lines) == 0
            assert ax.get_legend() is None
    else:
        assert supplied_orders["order_revenue"].tolist() == [100.0, 200.0, 900.0]
        assert supplied_units.to_dict("list") == {
            "order_units": [1, 3, 5], "order_count": [1, 1, 1],
        }
        for ax, positions in zip(fig.axes, [[400.0, 200.0], [3.0, 3.0]], strict=True):
            assert len(ax.lines) == 2
            for line, value in zip(ax.lines, positions, strict=True):
                np.testing.assert_allclose(
                    np.asarray(line.get_xdata(), dtype=float), [value, value],
                )
        heights = []
        for bar in fig.axes[0].patches:
            assert isinstance(bar, Rectangle)
            heights.append(bar.get_height())
        assert sum(heights) == 3
    pd.testing.assert_frame_equal(analyzer.dataframe, original)
    assert settings == settings_before
    assert matplotlib.rcParams == rc_before
    assert plt.isinteractive() == interactive_before
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("plotter, group_column", [
    (viz.plot_revenue_distribution_city, "city"),
    (viz.plot_revenue_distribution_category, "category"),
])
def test_boxplots_are_horizontal_without_warnings(settings, plotter, group_column):
    source = pd.DataFrame({
        group_column: ["A", "A", "B", "B"],
        "revenue": [10.0, 20.0, 30.0, 40.0],
    })
    summary = metrics.revenue_boxplot_summary(source, group_column)
    original = deepcopy(summary)
    figures_before = plt.get_fignums()
    rc_before = matplotlib.rcParams.copy()
    interactive_before = plt.isinteractive()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = plotter(summary, settings)
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == "Radintäkt [SEK]"
    assert ax.get_ylabel() == {"city": "Stad", "category": "Kategori"}[group_column]
    assert ax.get_title() == {
        "city": "Intäktsfördelning per stad",
        "category": "Intäktsfördelning per kategori",
    }[group_column]
    assert tuple(fig.get_size_inches()) == pytest.approx(settings["figure_size"])
    assert ax.get_facecolor() == to_rgba(settings["background_color"])
    assert len(ax.patches) == 2
    for box in ax.patches:
        assert isinstance(box, PathPatch)
        vertices = np.asarray(box.get_path().vertices, dtype=float)
        assert np.ptp(vertices[:, 0]) > np.ptp(vertices[:, 1])
    assert plt.get_fignums() == figures_before
    assert matplotlib.rcParams == rc_before
    assert plt.isinteractive() == interactive_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()
    pd.testing.assert_frame_equal(pd.DataFrame(summary), pd.DataFrame(original))


@pytest.mark.parametrize("plotter", [
    viz.plot_revenue_distribution_city,
    viz.plot_revenue_distribution_category,
])
def test_boxplots_handle_empty_summaries(settings, plotter):
    summary = []
    figures_before = plt.get_fignums()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = plotter(summary, settings)
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert not ax.axison
    assert [text.get_text() for text in ax.texts] == ["Inga data"]
    assert len(ax.patches) == 0
    assert len(ax.lines) == 0
    assert ax.get_legend() is None
    assert tuple(fig.get_size_inches()) == pytest.approx(settings["figure_size"])
    assert summary == []
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("plotter", [
    viz.plot_revenue_distribution_city,
    viz.plot_revenue_distribution_category,
])
@pytest.mark.parametrize("minimum_height", [4.0, 12.0])
def test_boxplots_wrap_original_missing_and_long_labels(
    settings, plotter, minimum_height,
):
    settings = {**settings, "figure_size": (7.0, minimum_height)}
    labels = [
        None,
        np.nan,
        pd.NA,
        (
            "En mycket lång ursprunglig etikett med flera ord som måste radbrytas "
            "utan att någon del av det ursprungliga namnet försvinner"
        ),
        "EttOvanligtLångtSammanhängandeNamnSomOcksåMåsteRadbrytas",
    ]
    summary: list[dict[str, Any]] = [
        {
            "label": label, "med": 5.0, "q1": 3.0, "q3": 7.0,
            "whislo": 1.0, "whishi": 9.0, "fliers": [20.0],
        }
        for label in labels
    ]
    original = deepcopy(summary)
    flier_lists = [item["fliers"] for item in summary]
    expected_labels = [
        fill("Ej angivet" if pd.isna(label) else str(label), width=24)
        for label in labels
    ]
    figures_before = plt.get_fignums()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = plotter(tuple(summary), settings)
        fig.canvas.draw()

    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_yticklabels()] == expected_labels
    assert all(
        len(line) <= 24 for label in expected_labels for line in label.splitlines()
    )
    line_count = sum(label.count("\n") + 1 for label in expected_labels)
    assert tuple(fig.get_size_inches()) == pytest.approx((
        7.0, max(minimum_height, 1.8 + 0.4 * line_count),
    ))
    pd.testing.assert_frame_equal(pd.DataFrame(summary), pd.DataFrame(original))
    assert all(
        item["fliers"] is fliers for item, fliers in zip(summary, flier_lists)
    )
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("plotter", [
    viz.plot_revenue_distribution_city,
    viz.plot_revenue_distribution_category,
])
def test_boxplots_draw_exact_prepared_statistics_and_styles(settings, plotter):
    # Deliberately not median-sorted; these values must not be recomputed.
    summary: list[dict[str, Any]] = [
        {
            "label": "High", "med": 50.0, "q1": 40.0, "q3": 65.0,
            "whislo": 20.0, "whishi": 80.0, "fliers": [110.0, -5.0],
        },
        {
            "label": None, "med": -10.0, "q1": -20.0, "q3": -2.0,
            "whislo": -30.0, "whishi": 5.0, "fliers": [-60.0],
        },
        {
            "label": "Constant", "med": 7.0, "q1": 7.0, "q3": 7.0,
            "whislo": 7.0, "whishi": 7.0, "fliers": [],
        },
    ]
    original = deepcopy(summary)
    figures_before = plt.get_fignums()

    with (
        patch.object(Axes, "bxp", autospec=True, side_effect=Axes.bxp) as bxp,
        patch.object(
            Axes, "boxplot", side_effect=AssertionError("Use prepared statistics"),
        ),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("error")
        fig = plotter(summary, settings)
        fig.canvas.draw()

    bxp.assert_called_once()
    assert bxp.call_args.kwargs["orientation"] == "horizontal"
    assert bxp.call_args.kwargs["patch_artist"] is True
    supplied_stats = bxp.call_args.args[1]
    expected_stats = deepcopy(original)
    expected_stats[1]["label"] = "Ej angivet"
    pd.testing.assert_frame_equal(
        pd.DataFrame(supplied_stats), pd.DataFrame(expected_stats),
    )
    assert all(
        supplied is not source and supplied["fliers"] is source["fliers"]
        for supplied, source in zip(supplied_stats, summary)
    )

    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_yticklabels()] == [
        "High", "Ej angivet", "Constant",
    ]
    assert len(ax.patches) == 3
    assert len(ax.lines) == 18
    for index, (box, stats) in enumerate(zip(ax.patches, original)):
        assert isinstance(box, PathPatch)
        vertices = np.asarray(box.get_path().vertices, dtype=float)
        assert vertices[:, 0].min() == pytest.approx(stats["q1"])
        assert vertices[:, 0].max() == pytest.approx(stats["q3"])
        assert np.ptp(vertices[:, 1]) > 0
        position = index + 1
        assert (vertices[:, 1].min() + vertices[:, 1].max()) / 2 == pytest.approx(
            position,
        )
        assert box.get_facecolor() == to_rgba(settings["main_color"])
        low_whisker, high_whisker, low_cap, high_cap, median, flier = (
            ax.lines[6 * index:6 * (index + 1)]
        )
        for line, expected_x in [
            (low_whisker, [stats["q1"], stats["whislo"]]),
            (high_whisker, [stats["q3"], stats["whishi"]]),
            (low_cap, [stats["whislo"], stats["whislo"]]),
            (high_cap, [stats["whishi"], stats["whishi"]]),
            (median, [stats["med"], stats["med"]]),
            (flier, stats["fliers"]),
        ]:
            np.testing.assert_allclose(
                np.asarray(line.get_xdata(), dtype=float), expected_x,
            )
        for line in (low_whisker, high_whisker, flier):
            np.testing.assert_allclose(
                np.asarray(line.get_ydata(), dtype=float),
                np.full(len(np.asarray(line.get_xdata())), position),
            )
        for line in (low_cap, high_cap, median):
            y = np.asarray(line.get_ydata(), dtype=float)
            assert y.min() < position < y.max()
        assert median.get_linewidth() == 3
        assert to_rgba(median.get_color()) == to_rgba(settings["median_color"])
        assert low_cap.get_linewidth() == high_cap.get_linewidth() == 2
        assert flier.get_alpha() == 0.5

    pd.testing.assert_frame_equal(pd.DataFrame(summary), pd.DataFrame(original))
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("method_name, group_column", [
    ("plot_revenue_distribution_city", "city"),
    ("plot_revenue_distribution_category", "category"),
])
@pytest.mark.parametrize("empty", [False, True])
def test_analyzer_boxplots_use_raw_row_revenue_summary(
    settings, monkeypatch, method_name, group_column, empty,
):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = pd.DataFrame({
        "order_id": ["Repeated"] * 5 + ["B", "B", "C", "C"],
        group_column: ["A"] * 5 + ["B", "B", None, None],
        "revenue": [1.0, 2.0, 3.0, 4.0, 100.0, 10.0, 30.0, 6.0, 8.0],
    })
    if empty:
        analyzer.dataframe = analyzer.dataframe.iloc[:0].copy()
    analyzer.settings = settings
    original = analyzer.dataframe.copy(deep=True)
    expected = metrics.revenue_boxplot_summary(analyzer.dataframe, group_column)
    prepare = Mock(wraps=metrics.revenue_boxplot_summary)
    render = Mock(wraps=getattr(viz, method_name))
    monkeypatch.setattr(metrics, "revenue_boxplot_summary", prepare)
    monkeypatch.setattr(viz, method_name, render)
    figures_before = plt.get_fignums()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = getattr(analyzer, method_name)()
        fig.canvas.draw()

    assert isinstance(fig, Figure)
    prepare.assert_called_once()
    assert prepare.call_args.args[0] is analyzer.dataframe
    assert prepare.call_args.args[1] == group_column
    render.assert_called_once()
    assert render.call_args.args[1] is settings
    pd.testing.assert_frame_equal(
        pd.DataFrame(render.call_args.args[0]), pd.DataFrame(expected),
    )
    ax = fig.axes[0]
    if empty:
        assert expected == []
        assert not ax.axison
        assert [text.get_text() for text in ax.texts] == ["Inga data"]
        assert len(ax.patches) == len(ax.lines) == 0
    else:
        assert expected[0] == {
            "label": "A", "med": 3.0, "q1": 2.0, "q3": 4.0,
            "whislo": 1.0, "whishi": 4.0, "fliers": [100.0],
        }
        assert len(ax.patches) == len(expected) == 3
        medians = ax.lines[4::6]
        assert len(medians) == len(expected)
        for median, stats in zip(medians, expected):
            np.testing.assert_allclose(
                np.asarray(median.get_xdata(), dtype=float),
                np.asarray([stats["med"], stats["med"]], dtype=float),
            )
        assert [tick.get_text() for tick in ax.get_yticklabels()] == [
            "A", "Ej angivet", "B",
        ]
    pd.testing.assert_frame_equal(analyzer.dataframe, original)
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()


@pytest.mark.parametrize("method_name, group_column", [
    ("plot_revenue_distribution_city", "city"),
    ("plot_revenue_distribution_category", "category"),
])
@pytest.mark.parametrize("invalid", [
    "missing_column", "non_numeric", "missing", "infinite",
])
def test_analyzer_boxplots_delegate_validation(
    settings, monkeypatch, method_name, group_column, invalid,
):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.settings = settings
    analyzer.dataframe = pd.DataFrame({
        group_column: ["A"],
        "revenue": [{
            "missing_column": 1.0,
            "non_numeric": "not revenue",
            "missing": np.nan,
            "infinite": np.inf,
        }[invalid]],
    })
    if invalid == "missing_column":
        analyzer.dataframe = analyzer.dataframe.drop(columns="revenue")
    original = analyzer.dataframe.copy(deep=True)
    with pytest.raises(ValueError) as helper_error:
        metrics.revenue_boxplot_summary(analyzer.dataframe, group_column)
    prepare = Mock(wraps=metrics.revenue_boxplot_summary)
    render = Mock(side_effect=AssertionError("Invalid data must not reach rendering"))
    monkeypatch.setattr(metrics, "revenue_boxplot_summary", prepare)
    monkeypatch.setattr(viz, method_name, render)
    figures_before = plt.get_fignums()

    with pytest.raises(ValueError) as analyzer_error:
        getattr(analyzer, method_name)()

    assert str(analyzer_error.value) == str(helper_error.value)
    prepare.assert_called_once()
    assert prepare.call_args.args[0] is analyzer.dataframe
    assert prepare.call_args.args[1] == group_column
    render.assert_not_called()
    pd.testing.assert_frame_equal(analyzer.dataframe, original)
    assert plt.get_fignums() == figures_before
    assert isinstance(plt.show, Mock)
    plt.show.assert_not_called()
