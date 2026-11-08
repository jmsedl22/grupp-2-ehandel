import warnings
from copy import deepcopy
from unittest.mock import Mock

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

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


@pytest.mark.parametrize("plotter, group_column", [
    (viz.plot_revenue_distribution_city, "city"),
    (viz.plot_revenue_distribution_category, "category"),
])
def test_boxplots_are_horizontal_without_warnings(plotter, group_column):
    source = pd.DataFrame({
        group_column: ["A", "A", "B", "B"],
        "revenue": [10.0, 20.0, 30.0, 40.0],
    })

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        plotter(source)
        fig = plt.gcf()
        fig.canvas.draw()

    assert len(fig.axes[0].patches) == 2
    for patch in fig.axes[0].patches:
        vertices = np.asarray(patch.get_path().vertices, dtype=float)
        assert np.ptp(vertices[:, 0]) > np.ptp(vertices[:, 1])
