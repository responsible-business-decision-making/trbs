"""
This file contains two functions which make a report of the information performed in the tool.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
from fpdf import FPDF
from vlinder.visualize import DependencyGraph, Visualize
from vlinder.optimize import Optimize
from vlinder.evaluate import Evaluate
from vlinder.appreciate import Appreciate


def chapter_title(pdf, title, rgb):
    """
    This function makes it possible to add a title to a chapter in a pdf
    :param pdf: the pdf where we want to apply the function on
    :param title: the title text
    :param rgb: the desired color in 3 number format
    :return: the updated pdf
    """
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(rgb[0], rgb[1], rgb[2])
    pdf.multi_cell(0, 10, title, 0, "C")
    pdf.ln(10)
    return pdf


def chapter_subtitle(pdf, subtitle):
    """
    This function makes it possible to add a subtitle to a chapter in a pdf
    :param pdf: the pdf where we want to apply the function on
    :param subtitle: the subtitle text
    :return: the updated pdf
    """
    subtitle = subtitle.replace("‘", "'")
    subtitle = subtitle.replace("’", "'")
    pdf.set_font(family="helvetica", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, subtitle, 0, "L")
    pdf.ln(10)
    return pdf


def title_page_title(pdf, title, rgb):
    """
    This function makes it possible to add a title to a title page in a pdf
    :param pdf: the pdf where we want to apply the function on
    :param title: the title text
    :param rgb: the desired color in 3 number format
    :return: the updated pdf
    """
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(rgb[0], rgb[1], rgb[2])
    pdf.multi_cell(0, 10, title, 0, "C")
    pdf.ln(10)
    return pdf


def title_page_subtitle(pdf, subtitle):
    """
    This function makes it possible to add a subtitle to a title page in a pdf
    :param pdf: the pdf where we want to apply the function on
    :param subtitle: the subtitle text
    :return: the updated pdf
    """
    pdf.set_font(family="helvetica", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, subtitle, 0, "C")
    pdf.ln(10)
    return pdf


def footer_page(pdf, name):
    """
    This function makes it possible to add a footer to a pdf, with desired text
    :param pdf: the pdf where we want to apply the function on
    :param name: the name of a case
    :param orientation: the orientation used for the pdf, i.e. Portrait or Landscape
    :return: the updated pdf
    """
    pdf.set_y(175)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(50, 10, name, 0, "L")
    x_position = pdf.w - 60  # Set x-position to the right edge of the page
    pdf.set_xy(x_position, pdf.get_y())  # Set the x-position of the multicell
    pdf.multi_cell(50, 0, f"Page {pdf.page_no()}", 0, "R")
    return pdf


def determine_position_images(image):
    """
    This function gives the possibility to place images at the desired position
    :param orientation: the desired orientation for PDF format; there is a choice between Portrait or Landscape
    :param image: information about the image
    :return: the right position
    """
    # Define the maximum dimensions for the image based on the orientation
    max_image_width = 180  # Example value, adjust as needed
    max_image_height = 120  # Example value, adjust as needed

    # Calculate the width and height to maintain the aspect ratio
    aspect_ratio = image.width / image.height
    if image.width > max_image_width or image.height > max_image_height:
        if aspect_ratio > 1:
            width_image = max_image_width
            height_image = max_image_width / aspect_ratio
            height_image = min(height_image, max_image_height)
        else:
            height_image = max_image_height
            width_image = max_image_height * aspect_ratio
    else:
        width_image = image.width
        height_image = image.height

    # Calculate the x position to center the image
    x_pos = (max_image_width - width_image) / 2 + 40  # Adjust the 10 as needed for padding
    y_pos = 50  # Adjust the 60 as needed for padding

    return width_image, height_image, x_pos, y_pos


class MakeReport:
    """
    This class deals with the transformation into a different format and export of output of an RBS case.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, output_path, name, input_dict, output_dict, visualize, page_dict):
        self.output_path = Path(output_path)
        self.folder_name = ""
        self.name = name
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.page_number = 1
        self.visualize = visualize
        self.visualizer = ""

        # set a default
        self.page_selection = {
            "title_page": True,
            "strategic_challenge": True,
            "key_outputs_theme": True,
            "decision_makers_options": True,
            "scenarios": True,
            "fixed_inputs": True,
            "dependencies": False,
            "weighted_appreciations": True,
            "add_optimize": False,
        }
        # update pages based
        self.page_selection.update({key: value for key, value in page_dict.items() if key in self.page_selection})

    def visualize_optimize(self, visual_request, key, **kwargs):
        """This function deals with the visualizations of the outcomes"""
        # Set a Visualize class only if this has not yet been initialised.
        if visual_request == "dependency_graph":
            dependency_tree = DependencyGraph(self.input_dict)
            return dependency_tree.draw_graph(key, **kwargs)

        self.visualizer = Visualize(
            self.input_dict,
            self.output_dict,
            len(self.input_dict["scenarios"])
            * len(self.input_dict["decision_makers_options"])
            * len(self.input_dict["key_outputs"]),
        )
        return self.visualizer.create_visual(visual_request, key, **kwargs)

    def make_title(self, target, scenario="", pos_series="", key_output="") -> str:
        """
        This function adds a title to a slide
        :param target: the desired slide where the title is wanted
        :param scenario: scenario of the output dict
        :param pos_series: position in series
        :param key_output: the selected key_output
        :return text: the desired title
        """
        if "title_" + target in self.input_dict["case_text_elements"]:
            text_element = "case_text_element"
        else:
            text_element = "generic_text_element"
        if target == "decision_makers_options":
            target = "dmo"
        if "title_" + target in self.input_dict[text_element + "s"]:
            if str(
                self.input_dict[text_element + "_value"][
                    list(self.input_dict[text_element + "s"]).index("title_" + target)
                ]
            ) != str("nan"):
                text = (
                    self.input_dict[text_element + "_value"][
                        list(self.input_dict[text_element + "s"]).index("title_" + target)
                    ]
                    + scenario
                    + pos_series
                    + key_output
                )
            else:
                text = "Not defined in template"

        else:
            text = "Not defined in template"
        return text

    def make_strategic_challenge(self) -> str:
        """
        This function adds an introduction to a slide
        :return: the strategic challenge
        """

        if "strategic_challenge" in self.input_dict["case_text_elements"]:
            if str(
                self.input_dict["case_text_element_value"][
                    list(self.input_dict["case_text_elements"]).index("strategic_challenge")
                ]
            ) != str("nan"):
                text = self.input_dict["case_text_element_value"][
                    list(self.input_dict["case_text_elements"]).index("strategic_challenge")
                ]
            else:
                text = "Not defined in template"
        else:
            text = "Not defined in template"
        return text

    def make_introduction(self, target) -> str:
        """
        This function adds an introduction to a slide
        :param target: the desired slide where the introduction is wanted
        :return: the desired introduction
        """

        if "intro_" + target in self.input_dict["case_text_elements"]:
            text_element = "case_text_element"
        else:
            text_element = "generic_text_element"
        if "intro_" + target in self.input_dict[text_element + "s"]:
            if str(
                self.input_dict[text_element + "_value"][
                    list(self.input_dict[text_element + "s"]).index("intro_" + target)
                ]
            ) != str("nan"):
                text = self.input_dict[text_element + "_value"][
                    list(self.input_dict[text_element + "s"]).index("intro_" + target)
                ]
            else:
                text = "Not defined in template"

        else:
            text = "Not defined in template"
        return text

    def make_slides_pdf(self, scenario):
        """
        This function present different visualisation on different slides in a PDF format
        :param scenario: the desired scenario which is used in the visualisations
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait or Landscape
        :return: the created report
        """
        # Make a temp directory for the images needed for the report
        if not os.path.exists("images"):
            os.mkdir("images")
        rgb = [0, 0, 120]
        pdf = FPDF(orientation="Landscape")
        pdf.set_title(f"Report of the {self.name} case")

        if self.page_selection["add_optimize"]:
            case_optimizer = Optimize(self.input_dict, self.output_dict)
            self.input_dict = case_optimizer.optimize_single_scenario(scenario, "Optimized DMO", 60000)
            case_evaluation = Evaluate(self.input_dict)
            self.output_dict = case_evaluation.evaluate_all_scenarios()

            case_appreciation = Appreciate(self.input_dict, self.output_dict)
            case_appreciation.appreciate_all_scenarios()
            self.visualize = self.visualize_optimize

        # Create title page
        if self.page_selection["title_page"]:
            pdf.add_page()
            pdf = title_page_title(pdf, "Report of the " + self.name + " case", rgb)
            # Search for a logo. if yes, place in the middle of the slide
            if os.path.exists("logos/" + self.name + ".jpeg"):
                # Open the image using Pillow
                image_path = "logos/" + self.name + ".jpeg"
                image = Image.open(image_path)
                width_image, height_image, x_pos, y_pos = determine_position_images(image)
                pdf.image(image_path, x=x_pos, y=y_pos, w=width_image, h=height_image)
            pdf = title_page_subtitle(pdf, "Responsible business decision making \n" + str(datetime.now().date()))

        if self.page_selection["strategic_challenge"]:
            # Create Strategic Challenge page
            pdf.add_page()
            pdf = chapter_title(pdf, "Strategic Challenge", rgb)
            pdf = chapter_subtitle(pdf, self.make_strategic_challenge())
            pdf = footer_page(pdf, self.name)

        # Create Input variables pages
        for input_tables in ["key_outputs_theme", "decision_makers_options", "scenarios", "fixed_inputs"]:
            if self.page_selection[input_tables]:
                if input_tables == "key_outputs_theme":
                    input_tables = "key_outputs"
                if input_tables in ("decision_makers_options", "scenarios"):
                    number_of_iterations = round((len(self.input_dict[input_tables[:-1] + "_value"][0]) / 10) + 0.5)
                else:
                    number_of_iterations = round((len(self.input_dict[input_tables]) / 10) + 0.5)
                for number_iteration in range(0, number_of_iterations):
                    pdf.add_page()
                    input_tables = "key_outputs_theme" if input_tables == "key_outputs" else input_tables
                    self.visualize("table", input_tables, save=True, number_iteration=number_iteration)
                    input_tables = "key_outputs" if input_tables == "key_outputs_theme" else input_tables
                    pdf = chapter_title(pdf, self.make_title(input_tables), rgb)
                    pdf = chapter_subtitle(pdf, self.make_introduction(input_tables))
                    # Search for the right table related to the input_table and place it in the middle of the slide
                    image_path = "images" + "/table" + input_tables + str(number_iteration) + ".png"
                    image = Image.open(image_path)
                    # Determine the position and size for the image
                    width_image, height_image, x_pos, y_pos = determine_position_images(image)
                    # Add the image to the PDF with the appropriate size and position
                    pdf.image(image_path, x=x_pos, y=y_pos, w=width_image, h=height_image)
                    pdf = footer_page(pdf, self.name)

        # Create for every key_output a dependency graph slide
        if self.page_selection["dependencies"]:
            for key_output in self.input_dict["key_outputs"]:
                pdf.add_page()
                pdf = chapter_title(pdf, f"The dependency graph for the key output: {key_output}", rgb)

                dep = DependencyGraph(self.input_dict)
                dep.draw_graph(selected_ko=key_output, save=True, sc_window_size="1920x1080")
                pdf.image("images/keyoutput_" + key_output + ".png", x=25, y=25, h=150)
                pdf = footer_page(pdf, self.name)

        # Create output slide with the weighted appreciations
        if self.page_selection["weighted_appreciations"]:
            for figure in ["weighted_appreciations", "scenario_appreciations"]:
                pdf.add_page()
                if figure == "weighted_appreciations":
                    pdf = chapter_title(
                        pdf,
                        "The decision maker option '"
                        + self.output_dict[scenario]["highest_weighted_dmo"]
                        + "' has the highest weighted appreciations for scenario: "
                        + scenario,
                        rgb,
                    )
                    self.visualize("barchart", "weighted_appreciations", scenario=scenario, stacked=True, save=True)
                else:
                    pdf = chapter_title(
                        pdf,
                        "Values of scenario appreciations",
                        rgb,
                    )
                    self.visualize("barchart", "scenario_appreciations", stacked=True, save=True)
                pdf.image("images" + "/figure_" + figure + ".png", x=25, y=50, w=250)
                pdf = footer_page(pdf, self.name)
        return pdf

    def create_report(self, scenario, path) -> str:
        """
        This function saves the created report out of the function make_slides at the desired location
        :param scenario: the desired scenario which is used in the visualisations
        :param path: the desired location where the report is saved
        :return: a success message including the location of the report
        """
        date_year = str(datetime.now().strftime("%Y-%m-%d"))
        date_hour = str(datetime.now().strftime("%H:%M:%S"))

        pdf = self.make_slides_pdf(scenario)
        filename = "Report " + self.name + " tRBS " + f'{date_year + " " + date_hour}.pdf'
        # Make a folder if it does not exist already
        if not os.path.exists(path):
            path.mkdir()
        pdf.output(str(path) + "/" + filename)
        text_finished = "The PDF report is generated and located at " + str(path) + "/" + filename
        # Remove the folder which contains the files for the report
        shutil.rmtree("images", ignore_errors=True)

        return text_finished
