import numpy as np
import anton.lights.config as config
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from anton.lights.audio.dsp import ExpFilter

# Create GUI window
app = QtGui.QApplication([])

class GuiThread(QThread):
    progress = pyqtSignal()
    
    def __init__(self, func, mel, pixels):
        super().__init__()
        self.func = func
        self.mel = mel
        self.pixels = pixels

    def run(self):
        self.func()
        self.progress.emit()

class VisGUI(pg.GraphicsView):
    
    active_color = '#16dbeb'
    inactive_color = '#FFFFFF'
    
    def __init__(self, effect_setter, melbank) -> None:
        super().__init__()
        
        self.effect_setter = effect_setter
        self.melbank = melbank
        
        layout = pg.GraphicsLayout(border=(100,100,100))
        self.setCentralItem(layout)
        self.show()
        self.setWindowTitle('Visualization')
        self.resize(800,600)
                
        # Mel filterbank plot
        fft_plot = layout.addPlot(title='Filterbank Output', colspan=3)
        fft_plot.setRange(yRange=[-0.1, 1.2])
        fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        x_data = np.array(range(1, config.N_FFT_BINS + 1))
        self.mel_curve = pg.PlotCurveItem()
        self.mel_curve.setData(x=x_data, y=x_data*0)
        fft_plot.addItem(self.mel_curve)
        
        # Visualization plot
        layout.nextRow()
        led_plot = layout.addPlot(title='Visualization Output', colspan=3)
        led_plot.setRange(yRange=[-5, 260])
        led_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        # Pen for each of the color channel curves
        r_pen = pg.mkPen((255, 30, 30, 200), width=4)
        g_pen = pg.mkPen((30, 255, 30, 200), width=4)
        b_pen = pg.mkPen((30, 30, 255, 200), width=4)
        # Color channel curves
        self.r_curve = pg.PlotCurveItem(pen=r_pen)
        self.g_curve = pg.PlotCurveItem(pen=g_pen)
        self.b_curve = pg.PlotCurveItem(pen=b_pen)
        # Define x data
        x_data = np.array(range(1, config.N_PIXELS + 1))
        self.r_curve.setData(x=x_data, y=x_data*0)
        self.g_curve.setData(x=x_data, y=x_data*0)
        self.b_curve.setData(x=x_data, y=x_data*0)
        # Add curves to plot
        led_plot.addItem(self.r_curve)
        led_plot.addItem(self.g_curve)
        led_plot.addItem(self.b_curve)
        # Frequency range label
        freq_label = pg.LabelItem('')
        # Frequency slider
        def freq_slider_change(tick):
            minf = freq_slider.tickValue(0)**2.0 * (config.MIC_RATE / 2.0)
            maxf = freq_slider.tickValue(1)**2.0 * (config.MIC_RATE / 2.0)
            t = 'Frequency range: {:.0f} - {:.0f} Hz'.format(minf, maxf)
            freq_label.setText(t)
            config.MIN_FREQUENCY = minf
            config.MAX_FREQUENCY = maxf
            melbank.update()
        freq_slider = pg.TickSliderItem(orientation='bottom', allowAdd=False)
        freq_slider.addTick((config.MIN_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        freq_slider.addTick((config.MAX_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        freq_slider.tickMoveFinished = freq_slider_change
        freq_label.setText('Frequency range: {} - {} Hz'.format(
            config.MIN_FREQUENCY,
            config.MAX_FREQUENCY))
        
        # Effect selection
        
            
        # Create effect "buttons" (labels with click event)
        self.energy_label = pg.LabelItem('Energy')
        self.scroll_label = pg.LabelItem('Scroll')
        self.spectrum_label = pg.LabelItem('Spectrum')
        self.energy_label.mousePressEvent = self.energy_click
        self.scroll_label.mousePressEvent = self.scroll_click
        self.spectrum_label.mousePressEvent = self.spectrum_click

        # Layout
        layout.nextRow()
        layout.addItem(freq_label, colspan=3)
        layout.nextRow()
        layout.addItem(freq_slider, colspan=3)
        layout.nextRow()
        layout.addItem(self.energy_label)
        layout.addItem(self.scroll_label)
        layout.addItem(self.spectrum_label)
        
        self.fft_plot_filter = ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                            alpha_decay=0.5, alpha_rise=0.99)
        
    def add_thread(self, thread):
        thread.connect(lambda: print('hi'))

    def handler(self):
        print('handling')
        return
        mel, pixels = data
        if mel is not None:
            x = np.linspace(config.MIN_FREQUENCY, config.MAX_FREQUENCY, len(mel))
            self.mel_curve.setData(x=x, y=self.fft_plot_filter.update(mel))
        # Plot the color channels
        self.r_curve.setData(y=pixels[0])
        self.g_curve.setData(y=pixels[1])
        self.b_curve.setData(y=pixels[2])
        app.processEvents()
        
    def energy_click(self,x):
        self.effect_setter('energy')
        self.energy_label.setText('Energy', color=VisGUI.active_color)
        self.scroll_label.setText('Scroll', color=VisGUI.inactive_color)
        self.spectrum_label.setText('Spectrum', color=VisGUI.inactive_color)
        
    def scroll_click(self,x):
        self.effect_setter('scroll')
        self.energy_label.setText('Energy', color=VisGUI.inactive_color)
        self.scroll_label.setText('Scroll', color=VisGUI.active_color)
        self.spectrum_label.setText('Spectrum', color=VisGUI.inactive_color)
        
    def spectrum_click(self,x):
        self.effect_setter('spectrum')
        self.energy_label.setText('Energy', color=VisGUI.inactive_color)
        self.scroll_label.setText('Scroll', color=VisGUI.inactive_color)
        self.spectrum_label.setText('Spectrum', color=VisGUI.active_color)