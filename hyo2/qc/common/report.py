import os
import datetime
import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class Report:
    """A class used to abstract a report"""

    def __init__(self, lib_name: str, lib_version: str):
        self.lib_name = lib_name
        self.lib_version = lib_version
        self.records = list()  # list of strings to be converted in human-readable form

    def __iadd__(self, record: str) -> "Report":
        """Add a record to the existing list of string records"""
        self.records.append(record)
        return self

    def display(self) -> None:
        """Print the content of the report on the monitor"""
        logger.info("<<<   START OF REPORT   >>>")
        for rec in self.records:
            logger.info("||| %s" % rec)
        logger.info("<<<    END OF REPORT    >>>")

    def generate_pdf(self, path: str, title: str = "Document", use_colors: bool = False, small: bool = False) -> bool:
        """Generate a multiple-page document, with passed title and list of strings"""

        # this function heavily relies on PySide for pdf creation, the import is local
        # to the function so that the class can still be used also without Pyside

        try:
            from PySide2 import QtGui
            from PySide2 import QtCore
            from PySide2 import QtPrintSupport

        except (ImportError, ValueError, IOError):
            logger.warning("PySide2 is not properly installed, thus you cannot create a pdf file")
            self.display()
            return False

        # some preliminary tests
        if len(path) == 0:
            logger.warning("The passed file path is empty")
            return False
        path = os.path.abspath(path)
        if '.pdf' not in path.lower():
            logger.warning("The passed file name has not the pdf extension: %s" % path)
            return False
        path = Helper.truncate_too_long(path)

        if len(self.records) == 0:
            logger.warning("The passed string list is empty")
            return False

        #
        # INITIAL SETTINGS
        #

        logger.debug("output: %s" % path)
        # delete the passed filename if it already exists
        if os.path.exists(path):
            os.remove(path)

        # the function will look for resources (images) on the same folder of this script
        media = os.path.abspath(os.path.join(os.path.dirname(__file__), 'media'))

        # prepare some drawing tools
        blue_pen = QtGui.QPen(QtGui.QColor(30, 30, 255))
        red_pen = QtGui.QPen(QtGui.QColor(255, 30, 30))
        green_pen = QtGui.QPen(QtGui.QColor(30, 200, 30))
        gray_pen = QtGui.QPen(QtGui.QColor(120, 120, 120))
        black_pen = QtGui.QPen(QtGui.QColor(30, 30, 30))
        if small:
            big_font = QtGui.QFont("Arial", 9)
            normal_font = QtGui.QFont("Arial", 6)
            bold_font = QtGui.QFont("Arial", 6, QtGui.QFont.Bold)
            small_font = QtGui.QFont("Arial", 5)
        else:
            big_font = QtGui.QFont("Arial", 10)
            normal_font = QtGui.QFont("Arial", 8)
            bold_font = QtGui.QFont("Arial", 8, QtGui.QFont.Bold)
            small_font = QtGui.QFont("Arial", 7)
        lc_flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter | QtCore.Qt.TextWordWrap
        cc_flags = QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap

        # create the printer for pdf
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setCreator("HydrOffice")
        printer.setDocName("HydrOffice.pdf")
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setOrientation(QtPrintSupport.QPrinter.Portrait)
        printer.setOutputFileName(path)
        page_rect = printer.pageRect()
        doc_width = page_rect.width()
        doc_height = page_rect.height()
        doc_margin = page_rect.x()
        # print(printer.getPageMargins(QtGui.QPrinter.DevicePixel))
        # logger.info("Canvas: %sx%s" % (doc_width, doc_height))
        # logger.info("Margin: %s" % doc_margin)

        # check if everything is ok
        if not printer.isValid():
            logger.warning("the PDF printer is not valid")
            return False

        #
        # ACTUAL PRINTING
        #

        page_nr = 1  # a counter for pages
        section_nr = 1
        row_counter = 1
        if small:
            row_height = 330
        else:
            row_height = 220  # this represents the height of a single row of text
        max_rows = (doc_height - 2 * doc_margin) / row_height
        hor_pad = row_height / 2

        # logger.info("rows for page: %i" % max_rows)

        # here we start painting to the printer
        painter = QtGui.QPainter()
        if not painter.begin(printer):
            logger.warning("not painter begin on printer")
            return False

        def print_page_template():
            """Internal helper function that print borders, logo, time stamp, etc."""
            # external border
            painter.setPen(gray_pen)
            border_area = QtCore.QRect(doc_margin, doc_margin,
                                       doc_width - 2*doc_margin, doc_height - 2*doc_margin)
            painter.drawRect(border_area)

            # make top-area
            top_area = QtCore.QRect(doc_margin, doc_margin,
                                    doc_width - 2*doc_margin, row_height*2)
            painter.drawRect(top_area)
            # logo
            hyo_logo = QtGui.QPixmap(os.path.join(media, 'poweredby.png'))
            # print("logo size: %sx%s" % (hyo_logo.width(), hyo_logo.height()))
            logo_area = QtCore.QRect(doc_width/2 - hyo_logo.width()/2,
                                     doc_margin + (row_height*2 - hyo_logo.height())/2,
                                     hyo_logo.width(), hyo_logo.height())
            painter.drawPixmap(logo_area, hyo_logo)

            # make bottom-area
            bottom_area = QtCore.QRect(doc_margin, doc_height - doc_margin - row_height,
                                       doc_width - 2*doc_margin, row_height)
            painter.drawRect(bottom_area)
            # time-stamp
            now_time = datetime.datetime.now()
            painter.setFont(small_font)
            painter.drawText(bottom_area, cc_flags, "time-stamp: %s, %s v.%s"
                             % (now_time.strftime("%a, %d %b %Y %H:%M:%S"), self.lib_name, self.lib_version))
            # page number
            page_area = QtCore.QRect(doc_width - doc_margin - 2*row_height, doc_height - doc_margin - row_height,
                                     2*row_height, row_height)
            # painter.drawRect(page_area)
            painter.drawText(page_area, lc_flags, "Page %s" % page_nr)

            # set back to 'normal' font
            painter.setPen(black_pen)
            painter.setFont(normal_font)
            return True

        print_page_template()

        row_area = QtCore.QRect(doc_margin + hor_pad, doc_margin,
                                doc_width - 2*doc_margin - 2*hor_pad, row_height)
        # painter.drawRect(row_area)

        first_page = True
        for content_item in self.records:

            # title document only for the first page
            if first_page:

                # document title
                if small:
                    row_counter = 4
                else:
                    row_counter = 3
                painter.setPen(blue_pen)
                painter.setFont(big_font)
                row_area.moveTo(row_area.x(), row_area.y() + row_counter*row_height)
                painter.drawText(row_area, cc_flags, title)
                # painter.drawRect(row_area)
                # row_counter += 1

                # set back to 'normal' font
                painter.setPen(black_pen)
                painter.setFont(normal_font)

                first_page = False

            # manage a new page creation
            if row_counter >= (max_rows - 4):

                if not printer.newPage():
                    logger.warning("Failed in flushing page to disk, disk full?")
                    return False

                page_nr += 1
                print_page_template()
                row_area = QtCore.QRect(doc_margin + hor_pad, doc_margin + row_height,
                                        doc_width - 2*doc_margin - 2*hor_pad, row_height)
                row_counter = 1

            row_area.moveTo(row_area.x(), row_area.y() + row_height)
            # painter.drawRect(row_area)

            last_item = content_item.split(' ')[-1]
            if last_item.isdigit():

                if int(last_item) > 0:  # troubles -> red pen
                    if use_colors:
                        painter.setPen(red_pen)
                    painter.drawText(row_area, lc_flags, "- " + content_item)
                    if use_colors:
                        painter.setPen(black_pen)

                else:  # all good -> black pen
                    painter.drawText(row_area, lc_flags, "- " + content_item)

            elif last_item == "[SKIP_REP]":  # skip report for this item
                if use_colors:
                    painter.setPen(gray_pen)
                painter.drawText(row_area, lc_flags, "- " + content_item.rsplit(' ', 1)[0])
                if use_colors:
                    painter.setPen(black_pen)

            elif last_item == "[CHECK]" or last_item == "[TOTAL]":  # the string is a section separator
                # leave an empty row
                row_area.moveTo(row_area.x(), row_area.y() + row_height)
                row_counter += 1
                # write a numbered sections
                painter.setFont(bold_font)
                painter.drawText(row_area, lc_flags,
                                 "%s. %s" % (section_nr, content_item.rsplit(' ', 1)[0]))  # cut the final token
                painter.setFont(normal_font)
                section_nr += 1

            elif last_item == "[SKIP_CHK]":  # the string is a section separator
                if use_colors:
                    painter.setPen(gray_pen)
                # leave an empty row
                row_area.moveTo(row_area.x(), row_area.y() + row_height)
                row_counter += 1
                # write a numbered sections
                painter.setFont(bold_font)
                painter.drawText(row_area, lc_flags,
                                 "%s. %s" % (section_nr, content_item.rsplit(' ', 1)[0]))  # cut the final token
                painter.setFont(normal_font)
                section_nr += 1
                if use_colors:
                    painter.setPen(black_pen)

            elif last_item == "OK":  # no issues, green ok
                if use_colors:
                    painter.setPen(green_pen)
                painter.drawText(row_area, lc_flags, content_item)
                if use_colors:
                    painter.setPen(black_pen)

            else:
                painter.drawText(row_area, lc_flags, content_item)

            row_counter += 1
            # print("page %s, row %s" % (page_nr, row_counter))

        #
        # FINISHING THE PRINTING
        #
        painter.end()

        return True
