import warnings
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
    (viz.plot_monthly_revenue, ["month", "category", "revenue"]),
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


def test_monthly_chart_preserves_dates_gaps_zero_and_missing_category(settings):
    source = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-10", "2024-03-01", "2024-02-03"]),
        "category": ["Books", "Books", None],
        "revenue": [0.0, 30.0, 20.0],
    })
    summary = metrics.monthly_category_summary(source)
    original = summary.copy(deep=True)

    fig = viz.plot_monthly_revenue(summary, settings)
    fig.canvas.draw()
    lines = {line.get_label(): line for line in fig.axes[0].lines}

    assert set(lines) == {"Books", "Ej angivet"}
    assert pd.to_datetime(np.asarray(lines["Books"].get_xdata())).tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    np.testing.assert_allclose(
        np.asarray(lines["Books"].get_ydata(), dtype=float),
        [0.0, np.nan, 30.0],
        equal_nan=True,
    )
    np.testing.assert_allclose(
        np.asarray(lines["Ej angivet"].get_ydata(), dtype=float),
        [np.nan, 20.0, np.nan],
        equal_nan=True,
    )
    pd.testing.assert_frame_equal(summary, original)


def test_analyzer_monthly_chart_uses_prepared_summary(settings):
    analyzer = CommerceAnalyzer.__new__(CommerceAnalyzer)
    analyzer.dataframe = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-03-01"]),
        "category": ["Books", "Books"],
        "revenue": [10.0, 30.0],
    })
    analyzer.settings = settings

    fig = analyzer.plot_monthly_revenue()
    fig.canvas.draw()

    assert isinstance(fig, Figure)
    np.testing.assert_allclose(
        np.asarray(fig.axes[0].lines[0].get_ydata(), dtype=float),
        [10.0, np.nan, 30.0],
        equal_nan=True,
    )


@pytest.mark.parametrize("counts, percentages", [
    ([], []),
    ([0, 0], [0.0, 0.0]),
    ([2, 1], [66.67, 33.33]),
])
def test_order_distribution_handles_empty_zero_and_nonempty(counts, percentages):
    summary = pd.DataFrame({
        "number of orders": counts,
        "percentages": percentages,
    }, index=[f"group{i}" for i in range(len(counts))])

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        viz.plot_order_value_distribution(summary)
        fig = plt.gcf()
        fig.canvas.draw()

    ax = fig.axes[0]
    assert len(ax.patches) == len(counts)
    if counts:
        assert ax.get_ylim()[1] > 0
        assert [text.get_text() for text in ax.texts] == [
            f"{percentage:.2f}%" for percentage in percentages
        ]
    else:
        assert not ax.axison
        assert [text.get_text() for text in ax.texts] == ["Inga data"]


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
