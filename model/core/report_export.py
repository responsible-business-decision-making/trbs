"""
This file contains two functions which make a powerpoint of the visualisations in the tool.
"""
from datetime import date, datetime
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_LEGEND_POSITION
import numpy as np

def iter_cells(table):
    """
    This function present different visualisation on different slides in a powerpoint format
    :param table: selected table
    """
    for row in table.rows:
        for cell in row.cells:
            yield cell

def make_slides(case, scenario):
    """
    This function present different visualisation on different slides in a powerpoint format
    :param case: selected case with all start and calculated values
    :param scenario: the desired scenario which is used in the visualisations
    """
    prs = Presentation()
    output_info = case.output_dict[scenario]
    input_info = case.input_dict
    x_loc, y_loc, x_weight, y_weight = Inches(0.5), Inches(2.5), Inches(9.0), Inches(2.0)
    x_loc_text, y_loc_text, x_weight_text, y_weight_text = Inches(1.0), Inches(1.5), Inches(8.0), Inches(2.0)

    # Generate title slide
    title_slide_layout = prs.slide_layouts[0]
    slide_title = prs.slides.add_slide(title_slide_layout)
    title = slide_title.shapes.title
    subtitle = slide_title.placeholders[1]
    title.text = "Executive summary of the " + case.name + " case"
    date_today = str(date.today().strftime("%d %B %Y"))
    subtitle.text = f"The Responsible Business Simulator \n {date_today}"

    # Create the table chart slide key outputs
    graph_slide_layout = prs.slide_layouts[5]
    slide_key_outputs = prs.slides.add_slide(graph_slide_layout)
    title = slide_key_outputs.shapes.title
    title.text = "The key outputs"
    slide_key_outputs.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    tx_box = slide_key_outputs.shapes.add_textbox(x_loc_text, y_loc_text, x_weight_text, y_weight_text)
    tf = tx_box.text_frame
    tf.text = 'The outputs upon which the decision maker will base his decision. A key output \n' \
              'is often referred to as KPI.'
    #  Data for table
    input_info_ko = input_info["key_outputs"]
    input_info_ko_th = input_info["key_output_theme"]
    shape = slide_key_outputs.shapes.add_table((len(input_info_ko) + 1), 2, x_loc, y_loc, x_weight, y_weight)
    table = shape.table
    headers_sum = ["Key outputs", "Theme"]
    for column, item in enumerate(headers_sum):
        cell = table.cell(0, column)
        cell.text = headers_sum[column]
    for column, table_name in enumerate([input_info_ko, input_info_ko_th]):
        for row in range(1, (len(input_info_ko) + 1)):
            cell = table.cell(row, column)
            cell.text = str(table_name[row - 1])
    for cell in iter_cells(table):
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(12)

    # Create the table chart slide decision maker's options
    graph_slide_layout = prs.slide_layouts[5]
    slide_dmo = prs.slides.add_slide(graph_slide_layout)
    title = slide_dmo.shapes.title
    title.text = "The decision maker's options"
    slide_dmo.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    tx_box = slide_dmo.shapes.add_textbox(x_loc_text, y_loc_text, x_weight_text, y_weight_text)
    tf = tx_box.text_frame
    tf.text = 'Set of potential sub-decisions, where each potential sub-decision is represented \n' \
              'by choosing a single value for the corresponding internal variable input'
    #  Data for table
    input_info_dmo = input_info["decision_makers_options"]
    input_info_dmo_values = input_info["decision_makers_option_value"]
    input_info_internal_value = input_info["internal_variable_inputs"]
    shape = slide_dmo.shapes.add_table(
        (len(input_info_internal_value) + 1), len(input_info_dmo) + 1, x_loc, y_loc, x_weight, y_weight
    )
    table = shape.table
    headers_sum = np.append(["Internal variable input"], input_info_dmo)
    #  Fill headers
    for column, item in enumerate(headers_sum):
        cell = table.cell(0, column)
        cell.text = headers_sum[column]
    #  Fill left column
    for row in range(1, len(input_info_internal_value) + 1):
        cell = table.cell(row, 0)
        cell.text = input_info_internal_value[row - 1]
    #  Fill rest of the table
    for column in range(1, len(input_info_dmo) + 1):
        for row in range(1, (len(input_info_internal_value) + 1)):
            cell = table.cell(row, column)
            value = float(input_info_dmo_values[column - 1][row - 1])
            cell.text = f"{value:.2f}"
    for cell in iter_cells(table):
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(12)


    # Create the table chart slide the scenarios
    graph_slide_layout = prs.slide_layouts[5]
    slide_scenarios = prs.slides.add_slide(graph_slide_layout)
    title = slide_scenarios.shapes.title
    title.text = "The scenario's"
    slide_scenarios.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    tx_box = slide_scenarios.shapes.add_textbox(x_loc_text, y_loc_text, x_weight_text, y_weight_text)
    tf = tx_box.text_frame
    tf.text = 'A coherent combination of future developments, where every single aspect \n' \
              'of external uncertainty is represented by choosing a single value for \n' \
              'the corresponding external variable input'
    #  Data for table
    input_info_scen = input_info["scenarios"]
    input_info_scen_values = input_info["scenario_value"]
    input_info_external_value = input_info["external_variable_inputs"]
    shape = slide_scenarios.shapes.add_table(
        (len(input_info_external_value) + 1), len(input_info_scen) + 1, x_loc, y_loc, x_weight, y_weight
    )
    table = shape.table
    headers_sum = np.append(["External variable input"], input_info_scen)
    #  Fill headers
    for column_header, item in enumerate(headers_sum):
        cell = table.cell(0, column_header)
        cell.text = headers_sum[column_header]
    #  Fill left column
    for row in range(1, len(input_info_external_value) + 1):
        cell = table.cell(row, 0)
        cell.text = input_info_external_value[row - 1]
    #  Fill rest of the table
    for column in range(1, len(input_info_scen) + 1):
        for row in range(1, (len(input_info_external_value) + 1)):
            cell = table.cell(row, column)
            value = float(input_info_scen_values[column - 1][row - 1])
            cell.text = f"{value:.2f}"
    for cell in iter_cells(table):
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(12)

    # Generate weighted appreciations slide
    weighted_app_slide_layout = prs.slide_layouts[5]
    slide_weighted_app = prs.slides.add_slide(weighted_app_slide_layout)
    title = slide_weighted_app.shapes.title
    title.text = "The resulting appreciations of different DMO’s for selected scenario " + scenario
    slide_weighted_app.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    #  Fill chart with data
    chart_data = CategoryChartData()
    chart_data.categories = output_info.keys()
    for series in list(output_info[list(output_info.keys())[0]]["weighted_appreciations"].keys()):
        values = [output_info[categorie]["weighted_appreciations"][series] for categorie in list(output_info.keys())]
        chart_data.add_series(series, values)
    #  implement chart on slide
    x_loc_chart, y_loc_chart, x_chart_weight, y_chart_weight = Inches(2), Inches(2), Inches(6), Inches(4.5)
    chart = slide_weighted_app.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_STACKED, x_loc_chart, y_loc_chart, x_chart_weight, y_chart_weight, chart_data
    ).chart
    #  color series on chart
    colors = [
        "#D04A02",
        "#EB8C00",
        "#FFB600",
        "#295477",
        "#299D8F",
        "#D04A02",
        "#EB8C00",
        "#FFB600",
        "#295477",
        "#299D8F",
        "#D04A02",
        "#EB8C00",
        "#FFB600",
        "#295477",
        "#299D8F",
    ]
    for index, series in enumerate(chart.series):
        fill = series.format.fill
        fill.solid()
        color_used = colors[index].lstrip("#")
        rgb = tuple(int(color_used[i: i + 2], 16) for i in (0, 2, 4))
        fill.fore_color.rgb = RGBColor(rgb[0], rgb[1], rgb[2])
    #  layout chart change
    category_axis = chart.category_axis
    category_axis.tick_labels.font.size = Pt(9)
    value_axis = chart.value_axis
    value_axis.maximum_scale = 100
    value_axis.major_unit = 20
    #  titles
    chart.chart_title.text_frame.text = "Values of weighted appreciations"
    chart.chart_title.text_frame.paragraphs[0].font.size = Pt(12)
    category_axis_title = chart.value_axis
    category_axis_title.axis_title.text_frame.text = "Appreciation value"
    category_axis_title.axis_title.text_frame.paragraphs[0].font.size = Pt(9)
    #  for implementing legend
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    chart.legend.horz_offset = 0.0
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(8)

    return prs


def create_report(case, scenario, path):
    """
    This function saves the created report out of the function make_powerpoint function in a desired location
    :param case: selected case with all start and calculated values
    :param scenario: the desired scenario which is used in the visualisations
    :param path: the desired location where the report is saved
    """
    prs = make_slides(case, scenario,)
    date_year = str(datetime.now().strftime("%Y-%m-%d"))
    date_hour = str(datetime.now().strftime("%Hh%Mm%Ss"))
    filename = "tRBS_" + case.name + f'_{date_year + "_" + date_hour}.pptx'
    prs.save(str(path) + "/" + filename)
    text_finished = "The powerpoint is generated and located at " + str(path) + "/" + filename
    return text_finished
