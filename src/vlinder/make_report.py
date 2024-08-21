"""
This file contains two functions which make a report of the information performed in the tool.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import cv2
from fpdf import FPDF


def chapter_title(pdf, title, rgb):
    """
    This function makes it possible to add a title to a chapter in a pdf
    :param pdf: the pdf where we want to apply the function on
    :param title: the title text
    :param rgb: the desired color in 3 number format
    :return: the updated pdf
    """
    pdf.set_font("Arial", "B", 16)
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
    pdf.set_font(family="Arial", size=12)
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
    pdf.set_font("Arial", "B", 22)
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
    pdf.set_font(family="Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, subtitle, 0, "C")
    pdf.ln(10)
    return pdf


def footer_page(pdf, name, orientation):
    """
    This function makes it possible to add a footer to a pdf, with desired text
    :param pdf: the pdf where we want to apply the function on
    :param name: the name of a case
    :param orientation: the orientation used for the pdf, i.e. Portrait or Landscape
    :return: the updated pdf
    """
    if orientation == "Portrait":
        pdf.set_y(250)
    else:
        pdf.set_y(175)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, name, 0, 0, "L")
    pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, "R")
    return pdf


def determine_position_images(orientation, image):
    """
    This function gives the possibility to place images at the desired position
    :param orientation: the desired orientation for PDF format; there is a choice between Portrait or Landscape
    :param image: information about the image
    :return: the right position
    """
    if orientation == "Landscape":
        max_image, width_image, x_pos = 800, 250, 150 - image.shape[1] / 5.32
    else:
        max_image, width_image, x_pos = 500, 150, 100 - image.shape[1] / 6.3
    return max_image, width_image, x_pos


class MakeReport:
    """
    This class deals with the transformation into a different format and export of output of an RBS case.
    """

    def __init__(self, output_path, name, input_dict, output_dict, visualize):
        self.output_path = Path(output_path)
        self.folder_name = ""
        self.name = name
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.page_number = 1
        self.visualize = visualize

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

    def make_slides_pdf(self, scenario, orientation):
        """
        This function present different visualisation on different slides in a PDF format
        :param scenario: the desired scenario which is used in the visualisations
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait or Landscape
        :return: the created report
        """
        # Make a temp directory for the images needed for the report
        os.mkdir("images")
        rgb = [0, 0, 120]
        pdf = FPDF(orientation=orientation)
        pdf.set_title("Report of the " + self.name + " case")
        # Create title page
        pdf.add_page()
        pdf = title_page_title(pdf, "Report of the " + self.name + " case", rgb)
        # Search for a logo. if yes, place in the middle of the slide
        if os.path.exists("logos/" + self.name + ".jpeg"):
            image = cv2.imread("logos/" + self.name + ".jpeg")
            max_image, width_image, x_pos = determine_position_images(orientation, image)
            if image.shape[1] > max_image:
                pdf.image("logos/" + self.name + ".jpeg", x=25, y=50, w=width_image)
            else:
                pdf.image("logos/" + self.name + ".jpeg", x=x_pos, y=50)
        pdf = title_page_subtitle(pdf, "Responsible business decision making \n" + str(datetime.now().date()))
        # Create Strategic Challenge page
        pdf.add_page()
        pdf = chapter_title(pdf, "Strategic Challenge", rgb)
        pdf = chapter_subtitle(pdf, self.make_strategic_challenge())
        pdf = footer_page(pdf, self.name, orientation)
        # Create Input variables pages
        for input_tables in ["key_outputs_theme", "decision_makers_options", "scenarios"]:
            pdf.add_page()
            self.visualize("table", input_tables, save=True)
            if input_tables == "key_outputs_theme":
                input_tables = "key_outputs"
            pdf = chapter_title(pdf, self.make_title(input_tables), rgb)
            pdf = chapter_subtitle(pdf, self.make_introduction(input_tables))
            # Search for the right table related to the input_table and place it in the middle of the slide
            image = cv2.imread("images" + "/table" + input_tables + ".png")
            max_image, width_image, x_pos = determine_position_images(orientation, image)
            if image.shape[1] > max_image:
                pdf.image("images" + "/table" + input_tables + ".png", x=25, y=60, w=width_image)
            else:
                pdf.image("images" + "/table" + input_tables + ".png", x=x_pos, y=60)
            pdf = footer_page(pdf, self.name, orientation)

        for input_tables in ["fixed_inputs"]:
            # If there are more than 10 fixed inputs it will generate a maximum of 10 per slide
            number_of_iterations = round((len(self.input_dict[input_tables]) / 10) + 0.5)
            for number_iteration in range(0, number_of_iterations):
                pdf.add_page()
                if number_of_iterations > 1:
                    pdf = chapter_title(
                        pdf,
                        self.make_title(input_tables)
                        + " "
                        + str(number_iteration + 1)
                        + "/"
                        + str(number_of_iterations),
                        rgb,
                    )
                else:
                    pdf = chapter_title(pdf, self.make_title(input_tables), rgb)
                pdf = chapter_subtitle(pdf, self.make_introduction(input_tables))
                self.visualize("table", input_tables, save=True, number_iteration=number_iteration)
                image = cv2.imread("images" + "/table" + input_tables + str(number_iteration) + ".png")
                max_image, width_image, x_pos = determine_position_images(orientation, image)
                if image.shape[1] > max_image:
                    pdf.image(
                        "images" + "/table" + input_tables + str(number_iteration) + ".png",
                        x=25,
                        y=50,
                        w=width_image,
                    )
                else:
                    pdf.image(
                        "images" + "/table" + input_tables + str(number_iteration) + ".png",
                        x=x_pos,
                        y=50,
                    )
                pdf = footer_page(pdf, self.name, orientation)
        # Create output slide with the weighted appreciations
        pdf.add_page()
        pdf = chapter_title(
            pdf,
            "The decision maker option '"
            + self.output_dict[scenario]["highest_weighted_dmo"]
            + "' has the highest weighted appreciations for scenario: "
            + scenario,
            rgb,
        )
        self.visualize("barchart", "weighted_appreciations", scenario=scenario, stacked=True, save=True)
        if orientation == "Portrait":
            pdf.image("images" + "/figure.png", x=25, y=50, w=150)
        else:
            pdf.image("images" + "/figure.png", x=25, y=50, w=250)
        pdf = footer_page(pdf, self.name, orientation)
        return pdf

    def create_report(self, scenario, orientation, path) -> str:
        """
        This function saves the created report out of the function make_slides at the desired location
        :param scenario: the desired scenario which is used in the visualisations
        :param path: the desired location where the report is saved
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait or Landscape
        :return: a success message including the location of the report
        """
        date_year = str(datetime.now().strftime("%Y-%m-%d"))
        date_hour = str(datetime.now().strftime("%H:%M:%S"))

        pdf = self.make_slides_pdf(scenario, orientation)
        filename = "Report " + self.name + " tRBS " + f'{date_year + " " + date_hour}.pdf'
        # Make a folder if it does not exist already
        if not os.path.exists(path):
            path.mkdir()
        pdf.output(str(path) + "/" + filename)
        text_finished = "The PDF report is generated and located at " + str(path) + "/" + filename
        # Remove the folder which contains the files for the report
        shutil.rmtree("images", ignore_errors=True)

        return text_finished
