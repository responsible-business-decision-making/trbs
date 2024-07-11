"""
This file contains two functions which make a report of the information performed in the tool.
"""

import os
import shutil
import cv2
from pathlib import Path
from datetime import datetime
from vlinder.presentation import PDF



class MakeReport:
    """
    This class deals with the transformation into a different format and export of output of an RBS case.
    """

    def __init__(self, output_path, name, input_dict, output_dict, visualize, random_number):
        self.output_path = Path(output_path)
        self.folder_name = ""
        self.name = name
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.page_number = 1
        self.visualize = visualize
        self.random_number = random_number

    def determine_position_images(self, orientation, image):
        """
        This function gives the possibility to place images at the right places which the desired orientation
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait of Landscape
        :param image: information about the image
        :return: the right position
        """
        if orientation == "Landscape":
            max_image, width_image, x_pos = 800, 250, 150 - image.shape[1] / 5.32
        else:
            max_image, width_image, x_pos = 500, 150, 100 - image.shape[1] / 6.3
        return max_image, width_image, x_pos

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
        :param target: the desired slide where the title is wanted
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
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait of Landscape
        :return: the created Presentation
        """
        os.mkdir(str(self.random_number))
        rgb = [0, 0, 120]
        pdf = PDF(orientation=orientation)
        pdf.set_title("Report of the " + self.name + " case")

        pdf.add_page()
        pdf.titlepage_title("Report of the " + self.name + " case", rgb)
        if os.path.exists("logos/" + self.name + ".jpeg"):
            image = cv2.imread("logos/" + self.name + ".jpeg")
            max_image, width_image, x_pos = self.determine_position_images(orientation, image)
            if image.shape[1] > max_image:
                pdf.image("logos/" + self.name + ".jpeg", x=25, y=50, w=width_image)
            else:
                pdf.image("logos/" + self.name + ".jpeg", x=x_pos, y=50)
        pdf.titlepage_subtitle("Responsible business decision making \n" + str(datetime.now().date()))
        pdf.add_page()
        pdf.chapter_title("Strategic Challenge", rgb)
        pdf.chapter_subtitle(self.make_strategic_challenge())
        pdf.footer_page(self.name, orientation)

        for input_tables in ["key_outputs_theme", "decision_makers_options", "scenarios"]:
            pdf.add_page()
            self.visualize("table", input_tables, save=True)
            if input_tables == "key_outputs_theme":
                input_tables = "key_outputs"
            pdf.chapter_title(self.make_title(input_tables), rgb)
            pdf.chapter_subtitle(self.make_introduction(input_tables))
            image = cv2.imread(str(self.random_number) + "/table" + input_tables + ".png")
            max_image, width_image, x_pos = self.determine_position_images(orientation, image)
            if image.shape[1] > max_image:
                pdf.image(str(self.random_number) + "/table" + input_tables + ".png", x=25, y=60, w=width_image)
            else:
                pdf.image(str(self.random_number) + "/table" + input_tables + ".png", x=x_pos, y=60)
            pdf.footer_page(self.name, orientation)

        for input_tables in ["fixed_inputs"]:
            number_of_iterations = round((len(self.input_dict[input_tables]) / 10) + 0.5)
            for number_iteration in range(0, number_of_iterations):
                pdf.add_page()
                if number_of_iterations > 1:
                    pdf.chapter_title(
                        self.make_title(input_tables)
                        + " "
                        + str(number_iteration + 1)
                        + "/"
                        + str(number_of_iterations),
                        rgb,
                    )
                else:
                    pdf.chapter_title(self.make_title(input_tables), rgb)
                pdf.chapter_subtitle(self.make_introduction(input_tables))
                self.visualize("table", input_tables, save=True, number_iteration=number_iteration)
                image = cv2.imread(str(self.random_number) + "/table" + input_tables + str(number_iteration) + ".png")
                max_image, width_image, x_pos = self.determine_position_images(orientation, image)
                if image.shape[1] > max_image:
                    pdf.image(
                        str(self.random_number) + "/table" + input_tables + str(number_iteration) + ".png",
                        x=25,
                        y=50,
                        w=width_image,
                    )
                else:
                    pdf.image(
                        str(self.random_number) + "/table" + input_tables + str(number_iteration) + ".png",
                        x=x_pos,
                        y=50,
                    )
                pdf.footer_page(self.name, orientation)

        pdf.add_page()
        pdf.chapter_title(
            "The decision maker option '"
            + self.output_dict[scenario]["highest_weighted_dmo"]
            + "' has the highest weighted appreciations for scenario: "
            + scenario,
            rgb,
        )
        self.visualize("barchart", "weighted_appreciations", scenario=scenario, stacked=True, save=True)
        if orientation == "Portrait":
            pdf.image(str(self.random_number) + "/figure.png", x=25, y=50, w=150)
        else:
            pdf.image(str(self.random_number) + "/figure.png", x=25, y=50, w=250)
        pdf.footer_page(self.name, orientation)
        return pdf

    def create_report(self, path, scenario, orientation) -> str:
        """
        This function saves the created report out of the function make_slides at the desired location
        :param scenario: the desired scenario which is used in the visualisations
        :param path: the desired location where the report is saved
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait of Landscape
        :return: the text where the PowerPoint is saved
        """
        date_year = str(datetime.now().strftime("%Y-%m-%d"))
        date_hour = str(datetime.now().strftime("%Hh%Mm%Ss"))

        pdf = self.make_slides_pdf(scenario, orientation)
        filename = "tRBS_" + self.name + f'_{date_year + "_" + date_hour}.pdf'
        pdf.output(str(path) + "/" + filename)
        text_finished = "The PDF presentation is generated and located at " + str(path) + "/" + filename
        # Remove the folder which contains the files for the presentation
        shutil.rmtree(str(self.random_number), ignore_errors=True)

        return text_finished
