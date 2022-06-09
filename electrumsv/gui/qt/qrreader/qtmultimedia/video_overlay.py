#!/usr/bin/env python3
#
# Electron Cash - lightweight Bitcoin client
# Copyright (C) 2019 Axel Gembe <derago@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import cast, Optional

from PyQt5.QtCore import QPoint, QSize, QRect, QRectF, Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QPen, QPainterPath, QColor, QTransform
from PyQt5.QtWidgets import QWidget

from .....qrreader.abstract_base import QrCodePoint, QrCodeResult

from .validator import QrReaderValidatorResult


class QrReaderVideoOverlay(QWidget):
    """
    Overlays the QR scanner results over the video
    """

    BG_RECT_PADDING = 10
    BG_RECT_CORNER_RADIUS = 10.0
    BG_RECT_OPACITY = 0.75

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)

        self.results: list[QrCodeResult] = []
        self.flip_x = False
        self.validator_results: Optional[QrReaderValidatorResult] = None
        self.crop: Optional[QRect] = None
        self.resolution: Optional[QSize] = None

        self.qr_outline_pen = QPen()
        self.qr_outline_pen.setColor(Qt.red)
        self.qr_outline_pen.setWidth(3)
        self.qr_outline_pen.setStyle(Qt.DotLine)

        self.text_pen = QPen()
        self.text_pen.setColor(Qt.black)

        self.bg_rect_pen = QPen()
        self.bg_rect_pen.setColor(Qt.black)
        self.bg_rect_pen.setStyle(Qt.DotLine)
        self.bg_rect_fill = QColor(255, 255, 255, int(255 * self.BG_RECT_OPACITY))

    def set_results(self, results: list[QrCodeResult], flip_x: bool,
            validator_results: QrReaderValidatorResult) -> None:
        self.results = results
        self.flip_x = flip_x
        self.validator_results = validator_results
        self.update()

    def set_crop(self, crop: QRect) -> None:
        self.crop = crop

    def set_resolution(self, resolution: QSize) -> None:
        self.resolution = resolution

    def paintEvent(self, _event: QPaintEvent) -> None:
        if not self.crop or not self.resolution:
            return

        painter = QPainter(self)

        # Keep a backup of the transform and create a new one
        transform = painter.worldTransform()

        # Set scaling transform
        transform = transform.scale(self.width() / self.resolution.width(),
                                    self.height() / self.resolution.height())

        # Compute the transform to flip the coordinate system on the x axis
        transform_flip = QTransform()
        if self.flip_x:
            transform_flip = transform_flip.translate(self.resolution.width(), 0.0)
            transform_flip = transform_flip.scale(-1.0, 1.0)

        # Small helper for tuple to QPoint
        def toqp(point: QrCodePoint) -> QPoint:
            return QPoint(point[0], point[1])

        # Starting from here we care about AA
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw all the QR code results
        for res in self.results:
            # NOTE(typing) Unsupported left operand type for * ("QTransform")
            painter.setWorldTransform(
                cast(QTransform, transform_flip * transform), # type: ignore[operator]
                False)

            # Draw lines between all of the QR code points
            pen = QPen(self.qr_outline_pen)
            validator_results = cast(QrReaderValidatorResult, self.validator_results)
            if res in validator_results.result_colors:
                pen.setColor(validator_results.result_colors[res])
            painter.setPen(pen)
            num_points = len(res.points)
            for i in range(0, num_points):
                i_n = i + 1

                line_from = toqp(res.points[i])
                line_from += self.crop.topLeft()

                line_to = toqp(res.points[i_n] if i_n < num_points else res.points[0])
                line_to += self.crop.topLeft()

                painter.drawLine(line_from, line_to)

            # Draw the QR code data
            # Note that we reset the world transform to only the scaled transform
            # because otherwise the text could be flipped. We only use transform_flip
            # to map the center point of the result.
            painter.setWorldTransform(transform, False)
            font_metrics = painter.fontMetrics()
            data_metrics = QSize(font_metrics.horizontalAdvance(res.data), font_metrics.capHeight())

            center_pos = toqp(res.center)
            center_pos += self.crop.topLeft()
            center_pos = transform_flip.map(center_pos)

            text_offset = QPoint(data_metrics.width(), data_metrics.height())
            text_offset = text_offset / 2
            text_offset.setX(-text_offset.x())
            center_pos += text_offset

            padding = self.BG_RECT_PADDING
            bg_rect_pos: QPoint = center_pos - QPoint(padding, data_metrics.height() + padding)
            # NOTE(typing) Unsupported operand types for * ("QSize" and "int")  [operator]
            bg_rect_size: QSize = data_metrics + \
                cast(QSize, (QSize(padding, padding) * 2)) # type: ignore[operator]
            bg_rect = QRect(bg_rect_pos, bg_rect_size)
            bg_rect_path = QPainterPath()
            radius = self.BG_RECT_CORNER_RADIUS
            bg_rect_path.addRoundedRect(QRectF(bg_rect), radius, radius, Qt.AbsoluteSize)
            painter.setPen(self.bg_rect_pen)
            painter.fillPath(bg_rect_path, self.bg_rect_fill)
            painter.drawPath(bg_rect_path)

            painter.setPen(self.text_pen)
            painter.drawText(center_pos, res.data)