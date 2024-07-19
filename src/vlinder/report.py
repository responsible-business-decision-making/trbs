from fpdf import FPDF


class PDF(FPDF):
    def chapter_title(self, title, rgb):
        self.set_font("Arial", "B", 16)
        self.set_text_color(rgb[0], rgb[1], rgb[2])
        self.multi_cell(0, 10, title, 0, "C")
        self.ln(10)

    def chapter_subtitle(self, subtitle):
        subtitle = subtitle.replace("‘", "'")
        subtitle = subtitle.replace("’", "'")
        self.set_font(family="Arial", size=12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, subtitle, 0, "L")
        self.ln(10)

    def title_page_title(self, title, rgb):
        self.set_font("Arial", "B", 22)
        self.set_text_color(rgb[0], rgb[1], rgb[2])
        self.multi_cell(0, 10, title, 0, "C")
        self.ln(10)

    def title_page_subtitle(self, subtitle):
        self.set_font(family="Arial", size=12)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, subtitle, 0, "C")
        self.ln(10)

    def footer_page(self, name, orientation):
        if orientation == "Portrait":
            self.set_y(250)
        else:
            self.set_y(175)
        self.set_font("Arial", "I", 8)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, name, 0, 0, "L")
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")
