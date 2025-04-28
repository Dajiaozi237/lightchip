from si_fab import all as pdk
from ipkiss3 import all as i3
# Importing the technology and IPKISS
from si_fab import all as pdk
from ipkiss3 import all as i3
from si_fab.components.waveguides.wire import SiWireWaveguideTemplate
import math
import numpy as np
import sys  # 导入sys模块
from GACDC_Pcell import GACDC_HT, GACDC_HT_ScanField, GACDCFourChannel
from CascadedWBG_Pcell import LongCascadedWBG, CompactCascadedWBG,CompactCascadedWBG_HV
from RingDC_Pcell import BPFDcWaveguide, DcWaveguide, BPFDcRing
from cell_ringDoubleBus import Ring_doubleBus,Ring_doubleBus_160,Ring_doubleBus_180
from PBS_col1 import customPBS

class TempPort(i3.PCell):
    """
       in       ---------------------------------    out
    """
    class Layout(i3.LayoutView):
        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="in", position=(0.0, 0.0), angle=180.0)
            ports += i3.OpticalPort(name="out", position=(0.0, 0.0), angle=0.0)
            return ports

class CompactIntegratedSource(i3.PCell):
    """
    Integrated Source with following components:
    1. 12mm long single mode waveguide to generate single photon
    2. cascaded WBG to suppress the pump
    3. GACDC to extract photon
    """
    _name_prefix = "IntegratedSource"
    gap_x = i3.PositiveNumberProperty(default=60, doc="gap between components")
    gap_y = i3.PositiveNumberProperty(default=60, doc="gap between components")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="lambda of pump")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    WBG_period = i3.PositiveNumberProperty(default=0.2965, doc="grating period of WBG ")
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    GAP_WBG_WG_Y = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    GAP_WBG_WG_X = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    m = i3.PositiveNumberProperty(default=1, doc=" ")
    radius = i3.PositiveNumberProperty(default=28, doc="radius of the disk")
    spacing = i3.PositiveNumberProperty(default=0.22 + 0.45,
                                        doc="spacing between centerline of bus waveguide and edge of the disk")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap_x = self.gap_x
            gap_y = self.gap_y
            # calculate grating period via lambda
            # factor = 1
            # period_signal = self.lambda_signal/factor
            # period_idler = self.lambda_idler/factor
            total_length = self.total_length
            EBL_scan_filed_length = self.EBL_scan_filed_length
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            lambda_pump = self.lambda_pump
            GAP_WBG_WG_Y = self.GAP_WBG_WG_Y
            m = self.m
            radius=self.radius
            spacing=self.spacing
            insts_insts = {
                'WaveguideSource': BPFDcWaveguide(lambda_pump=lambda_pump, total_length=total_length),
                'Cascaded_WBG': CompactCascadedWBG(period=self.WBG_period),
                'output': GACDCFourChannel(
                    lambda_signal_1=lambda_signal_1,
                    lambda_signal_2=lambda_signal_2,
                    lambda_idler_1=lambda_idler_1,
                    lambda_idler_2=lambda_idler_2
                ),
                'Ring': Ring_doubleBus_180(),
            }
            # if m == 1:
            #     insts_insts['Cascaded_WBG']=CompactCascadedWBG(period=0.2969)
            # elif m == 2:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG(period=0.2998)

            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('WaveguideSource:in', (0, 0)),
                i3.PlaceRelative('Cascaded_WBG:in', 'WaveguideSource:out',
                                 (EBL_scan_filed_length-20, -150)),
                i3.PlaceRelative('Ring:in', 'Cascaded_WBG:out',
                                 (EBL_scan_filed_length/2 , 0)),
                i3.FlipV('output'),
                i3.PlaceRelative('output:in', 'Ring:drop',
                                 (EBL_scan_filed_length /2-30, 50)),
                i3.ConnectManhattan([
                    ('WaveguideSource:out', 'Cascaded_WBG:in'),
                    ('Cascaded_WBG:out','Ring:in',),
                    ('output:in', 'Ring:drop'),
                ],
                    bend_radius=20
                ),
            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'WaveguideSource:in': 'in',
                                         # 'WaveguideSource:DC_out10': 'DC_out10',
                                         'output:signal_1': 'signal_1',
                                         'output:signal_2': 'signal_2',
                                         'output:idler_1': 'idler_1',
                                         'output:idler_2': 'idler_2',
                                         'output:through': 'through',
                                         'WaveguideSource:through': 'input_through',
                                         'WaveguideSource:add': 'input_add',
                                         'Ring:through':'ringthrough',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'WaveguideSource:elec1': 'elec1',
                                             'WaveguideSource:elec2': 'elec2',
                                             'Cascaded_WBG:elec1': 'elec3',
                                             'Cascaded_WBG:elec2': 'elec4',
                                             'Cascaded_WBG:elec3': 'elec5',
                                             'Cascaded_WBG:elec4': 'elec6',
                                             'Cascaded_WBG:elec5': 'elec7',
                                             'Cascaded_WBG:elec6': 'elec8',
                                             'Cascaded_WBG:elec7': 'elec9',
                                             'Cascaded_WBG:elec8': 'elec10',
                                             'Ring:elec1':'elec11',
                                             'Ring:elec2':'elec12',
                                             'output:elec1': 'elec13',
                                             'output:elec3': 'elec16',
                                             'output:elec5': 'elec17',
                                             'output:elec7': 'elec20',
                                             'output:elec2': 'elec14',
                                             'output:elec4': 'elec15',
                                             'output:elec6': 'elec18',
                                             'output:elec8': 'elec19',
                                         })
            return ports

class CompactIntegratedSourcePBSTMWBG(i3.PCell):
    """
    Integrated Source with following components:
    1. 12mm long single mode waveguide to generate single photon
    2. cascaded WBG to suppress the pump
    3. GACDC to extract photon
    4.PBS
    5.TM WBG
    """
    _name_prefix = "IntegratedSource"
    gap_x = i3.PositiveNumberProperty(default=60, doc="gap between components")
    gap_y = i3.PositiveNumberProperty(default=60, doc="gap between components")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="lambda of pump")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    WBG_period = i3.PositiveNumberProperty(default=0.299, doc="grating period of WBG ")
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    GAP_WBG_WG_Y = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    GAP_WBG_WG_X = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    m = i3.PositiveNumberProperty(default=1, doc=" ")
    radius = i3.PositiveNumberProperty(default=27.5, doc="radius of the disk")
    spacing = i3.PositiveNumberProperty(default=0.25 + 0.5,
                                        doc="spacing between centerline of bus waveguide and edge of the disk")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap_x = self.gap_x
            gap_y = self.gap_y
            # calculate grating period via lambda
            # factor = 1
            # period_signal = self.lambda_signal/factor
            # period_idler = self.lambda_idler/factor
            total_length = self.total_length
            EBL_scan_filed_length = self.EBL_scan_filed_length
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            lambda_pump = self.lambda_pump
            # WBG_period_1 = self.WBG_period_1
            GAP_WBG_WG_Y = self.GAP_WBG_WG_Y
            m = self.m
            radius=self.radius
            spacing=self.spacing
            PBS = customPBS(
                Length1=8.5
            )
            insts_insts = {
                'PBS': PBS,
                'WaveguideSource': BPFDcWaveguide(lambda_pump=lambda_pump, total_length=total_length),
                'Cascaded_WBG': CompactCascadedWBG(period=self.WBG_period),
                # 'Cascaded_WBG': CompactCascadedWBG(),
                'output': GACDCFourChannel(
                    lambda_signal_1=lambda_signal_1,
                    lambda_signal_2=lambda_signal_2,
                    lambda_idler_1=lambda_idler_1,
                    lambda_idler_2=lambda_idler_2
                ),
                'Ring': Ring_doubleBus(),
            }

            insts_specs = [
                i3.Place('PBS:in', (0, 0)),
                i3.PlaceRelative('WaveguideSource:in', 'PBS:out2',
                                 (50, 0)),
                i3.PlaceRelative('Cascaded_WBG:in', 'WaveguideSource:out',
                                 (EBL_scan_filed_length, 0)),
                # i3.FlipV('Ring'),
                i3.PlaceRelative('Ring:in', 'Cascaded_WBG:out',
                                 (EBL_scan_filed_length/2 , 0)),
                # i3.PlaceRelative('input_through:out', 'WaveguideSource:through',
                #                  (0, -EBL_scan_filed_length / 10)),
                # i3.PlaceRelative('input_add:out', 'WaveguideSource:add',
                #                  (EBL_scan_filed_length / 50 + 10, -EBL_scan_filed_length / 10)),
                i3.FlipV('output'),
                i3.PlaceRelative('output:in', 'Ring:drop',
                                 (EBL_scan_filed_length /2, 50)),
                i3.ConnectManhattan([
                    ('PBS:out2', 'WaveguideSource:in'),
                    ('WaveguideSource:out', 'Cascaded_WBG:in'),
                    ('Cascaded_WBG:out','Ring:in',),
                    ('output:in', 'Ring:drop'),
                    # ('input_through:out', 'WaveguideSource:through'),
                    # ('input_add:out', 'WaveguideSource:add'),
                ],
                    bend_radius=20
                ),
                # i3.ConnectManhattan([
                #     ('WaveguideSource:out', 'Cascaded_WBG:in')
                # ],
                #     bend_radius=20,
                #     control_points=[i3.START + (50, 100)]
                # ),
            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'WaveguideSource:in': 'in',
                                         # 'WaveguideSource:DC_out10': 'DC_out10',
                                         'output:signal_1': 'signal_1',
                                         'output:signal_2': 'signal_2',
                                         'output:idler_1': 'idler_1',
                                         'output:idler_2': 'idler_2',
                                         'output:through': 'through',
                                         'WaveguideSource:through': 'input_through',
                                         'WaveguideSource:add': 'input_add',
                                         'Ring:through':'ringthrough',
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'WaveguideSource:elec1': 'elec1',
                                             'WaveguideSource:elec2': 'elec2',
                                             'Cascaded_WBG:elec1': 'elec3',
                                             'Cascaded_WBG:elec2': 'elec4',
                                             'Cascaded_WBG:elec3': 'elec5',
                                             'Cascaded_WBG:elec4': 'elec6',
                                             'Cascaded_WBG:elec5': 'elec7',
                                             'Cascaded_WBG:elec6': 'elec8',
                                             'Cascaded_WBG:elec7': 'elec9',
                                             'Cascaded_WBG:elec8': 'elec10',
                                             'Ring:elec1':'elec11',
                                             'Ring:elec2':'elec12',
                                             'output:elec1': 'elec13',
                                             'output:elec3': 'elec16',
                                             'output:elec5': 'elec17',
                                             'output:elec7': 'elec20',
                                             'output:elec2': 'elec14',
                                             'output:elec4': 'elec15',
                                             'output:elec6': 'elec18',
                                             'output:elec8': 'elec19',
                                         })
            return ports


class CompactIntegratedSourceRing(i3.PCell):
    """
    Integrated Source with following components:
    1. 12mm long single mode waveguide to generate single photon
    2. cascaded WBG to suppress the pump
    3. GACDC to extract photon
    """
    _name_prefix = "IntegratedSource"
    gap_x = i3.PositiveNumberProperty(default=60, doc="gap between components")
    gap_y = i3.PositiveNumberProperty(default=60, doc="gap between components")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="lambda of pump")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap_x = self.gap_x
            gap_y = self.gap_y
            # calculate grating period via lambda
            # factor = 1
            # period_signal = self.lambda_signal/factor
            # period_idler = self.lambda_idler/factor
            total_length = self.total_length
            EBL_scan_filed_length = self.EBL_scan_filed_length
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            lambda_pump = self.lambda_pump
            insts_insts = {
                'WaveguideSource': BPFDcRing(lambda_pump=lambda_pump),
                'Cascaded_WBG': CompactCascadedWBG(),
                'output': GACDCFourChannel(
                    lambda_signal_1=lambda_signal_1,
                    lambda_signal_2=lambda_signal_2,
                    lambda_idler_1=lambda_idler_1,
                    lambda_idler_2=lambda_idler_2
                ),
                'input_through': TempPort()
            }

            insts_specs = [
                # i3.ConnectManhattan('bend90_ua:in', 'bend90_ud:out'),
                i3.Place('WaveguideSource:in', (0, 0)),
                i3.PlaceRelative('Cascaded_WBG:in', 'WaveguideSource:out',
                                 (EBL_scan_filed_length, -EBL_scan_filed_length/10)),
                i3.PlaceRelative('input_through:out', 'WaveguideSource:through',
                                 (0, -EBL_scan_filed_length / 10)),
                i3.FlipV('output'),
                i3.PlaceRelative('output:in', 'Cascaded_WBG:out',
                                 (EBL_scan_filed_length, -EBL_scan_filed_length/5)),
                i3.ConnectManhattan([
                    ('WaveguideSource:out', 'Cascaded_WBG:in'),
                    ('output:in', 'Cascaded_WBG:out'),
                    ('input_through:out', 'WaveguideSource:through')
                ],
                    bend_radius=20
                ),
            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'WaveguideSource:in': 'in',
                                         'WaveguideSource:DC_out10': 'DC_out10',
                                         'WaveguideSource:DC_2_out10': 'DC_2_out10',
                                         'output:signal_1': 'signal_1',
                                         'output:signal_2': 'signal_2',
                                         'output:idler_1': 'idler_1',
                                         'output:idler_2': 'idler_2',
                                         'output:through': 'through',
                                         'input_through:in': 'input_through'
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'WaveguideSource:elec1': 'elec1',
                                             'WaveguideSource:elec2': 'elec2',
                                             'WaveguideSource:elec3': 'elec3',
                                             'WaveguideSource:elec4': 'elec4',
                                             'Cascaded_WBG:elec1': 'elec8',
                                             'Cascaded_WBG:elec2': 'elec9',
                                             'Cascaded_WBG:elec3': 'elec7',
                                             'Cascaded_WBG:elec4': 'elec10',
                                             'Cascaded_WBG:elec5': 'elec6',
                                             'Cascaded_WBG:elec6': 'elec11',
                                             'Cascaded_WBG:elec7': 'elec5',
                                             'Cascaded_WBG:elec8': 'elec12',
                                             'output:elec1': 'elec13',
                                             'output:elec3': 'elec14',
                                             'output:elec5': 'elec15',
                                             'output:elec7': 'elec16',
                                             'output:elec2': 'elec20',
                                             'output:elec4': 'elec19',
                                             'output:elec6': 'elec18',
                                             'output:elec8': 'elec17',
                                         })
            return ports


class CompactIntegratedSourceElectricFlip(i3.PCell):
    """
    Integrated Source with following components:
    1. 12mm long single mode waveguide to generate single photon
    2. cascaded WBG to suppress the pump
    3. GACDC to extract photon
    """
    _name_prefix = "IntegratedSource"
    gap_x = i3.PositiveNumberProperty(default=60, doc="gap between components")
    gap_y = i3.PositiveNumberProperty(default=60, doc="gap between components")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="lambda of pump")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    WBG_period = i3.PositiveNumberProperty(default=0.2965, doc=" ")
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    GAP_WBG_WG_Y = i3.FloatProperty(default=5, doc="vertical gap between WBG and WaveguideSource")
    GAP_WBG_WG_X = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    GAP_GACDC_WBG_Y = i3.FloatProperty(default=100, doc="vertical gap between WBG and GACDC")
    m = i3.PositiveNumberProperty(default=1, doc=" ")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            lambda_pump = self.lambda_pump
            # WBG_period = self.WBG_period
            m = self.m
            gap_x = self.gap_x
            gap_y = self.gap_y
            # calculate grating period via lambda
            # factor = 1
            # period_signal = self.lambda_signal/factor
            # period_idler = self.lambda_idler/factor
            total_length = self.total_length
            EBL_scan_filed_length = self.EBL_scan_filed_length
            GAP_WBG_WG_Y = self.GAP_WBG_WG_Y
            GAP_GACDC_WBG_Y = self.GAP_GACDC_WBG_Y
            insts_insts = {
                'WaveguideSource': BPFDcWaveguide(
                    lambda_pump=lambda_pump,
                    total_length=total_length
                ),
                'Cascaded_WBG': CompactCascadedWBG(period=self.WBG_period),
                'output': GACDCFourChannel(
                    lambda_signal_1=lambda_signal_1,
                    lambda_signal_2=lambda_signal_2,
                    lambda_idler_1=lambda_idler_1,
                    lambda_idler_2=lambda_idler_2
                ),
                'Ring': Ring_doubleBus_160(),
                # 'input_through': TempPort(),
                # 'input_add': TempPort(),
            }

            # if m == 1:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.15)
            # elif m == 2:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.2969)
            # elif m == 3:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.2940)

            insts_specs = [
                i3.Place('WaveguideSource:in', (0, 0)),
                i3.PlaceRelative('Cascaded_WBG:in', 'WaveguideSource:out',
                                 (EBL_scan_filed_length-20, -100)),
                i3.FlipV('output'),
                i3.PlaceRelative('output:in', 'Cascaded_WBG:out',
                                 (EBL_scan_filed_length-40 , GAP_GACDC_WBG_Y)),
                i3.PlaceRelative('Ring:in', 'output:in',
                                 (-400,-100)),
                # i3.ConnectManhattan([
                #     ('Cascaded_WBG:out', 'Ring:in'),
                #     ('output:in', 'Ring:drop'),
                #     # ('input_through:out', 'WaveguideSource:through'),
                #     # ('input_add:out', 'WaveguideSource:add'),
                # ],
                #     bend_radius=20
                # ),
                i3.ConnectManhattan([
                    ('Ring:in', 'Cascaded_WBG:out'),
                    ('output:in', 'Ring:drop'),
                ],
                    bend_radius=20
                ),
                i3.ConnectManhattan([
                    ('WaveguideSource:out', 'Cascaded_WBG:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (50, 100)]
                ),
            ]
            #     i3.ConnectManhattan([
            #         ('WaveguideSource:out', 'Ring:in')
            #     ],
            #         bend_radius=20,
            #         control_points=[i3.START + (50, 100)]
            #     ),
            # ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'WaveguideSource:in': 'in',
                                         # 'WaveguideSource:DC_out10': 'DC_out10',
                                         'output:signal_1': 'signal_1',
                                         'output:signal_2': 'signal_2',
                                         'output:idler_1': 'idler_1',
                                         'output:idler_2': 'idler_2',
                                         'output:through': 'through',
                                         'WaveguideSource:through': 'input_through',
                                         'WaveguideSource:add': 'input_add',
                                         'Ring:through':'ringthrough'
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'WaveguideSource:elec1': 'elec1',
                                             'WaveguideSource:elec2': 'elec2',
                                             'Ring:elec1': 'elec11',
                                             'Ring:elec2': 'elec12',
                                             'Cascaded_WBG:elec1': 'elec3',
                                             'Cascaded_WBG:elec2': 'elec4',
                                             'Cascaded_WBG:elec3': 'elec5',
                                             'Cascaded_WBG:elec4': 'elec6',
                                             'Cascaded_WBG:elec5': 'elec7',
                                             'Cascaded_WBG:elec6': 'elec8',
                                             'Cascaded_WBG:elec7': 'elec9',
                                             'Cascaded_WBG:elec8': 'elec10',
                                             'output:elec1': 'elec13',
                                             'output:elec3': 'elec16',
                                             'output:elec5': 'elec17',
                                             'output:elec7': 'elec20',
                                             'output:elec2': 'elec14',
                                             'output:elec4': 'elec15',
                                             'output:elec6': 'elec18',
                                             'output:elec8': 'elec19',
                                         })
            return ports

class CompactIntegratedSourceElectricFlip_HV(i3.PCell):
    """
    Integrated Source with following components:
    1. 12mm long single mode waveguide to generate single photon
    2. cascaded WBG to suppress the pump
    3. GACDC to extract photon
    """
    _name_prefix = "IntegratedSource"
    gap_x = i3.PositiveNumberProperty(default=60, doc="gap between components")
    gap_y = i3.PositiveNumberProperty(default=60, doc="gap between components")
    lambda_pump = i3.PositiveNumberProperty(default=1.55, doc="lambda of pump")
    lambda_signal_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_signal_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of signal photon")
    lambda_idler_1 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    lambda_idler_2 = i3.PositiveNumberProperty(default=1.55, doc="lambda of idler photon")
    WBG_period = i3.PositiveNumberProperty(default=0.2965, doc=" ")
    EBL_scan_filed_length = i3.PositiveNumberProperty(default=1000, doc="EBL_scan_filed_length")
    heater_open = i3.BoolProperty(default='True', doc='False for no heater')
    total_length = i3.PositiveNumberProperty(default=11000, doc="length of the spiral")
    GAP_WBG_WG_Y = i3.FloatProperty(default=5, doc="vertical gap between WBG and WaveguideSource")
    GAP_WBG_WG_X = i3.FloatProperty(default=0, doc="vertical gap between WBG and WaveguideSource")
    GAP_GACDC_WBG_Y = i3.FloatProperty(default=100, doc="vertical gap between WBG and GACDC")
    m = i3.PositiveNumberProperty(default=1, doc=" ")
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            lambda_signal_1 = self.lambda_signal_1
            lambda_signal_2 = self.lambda_signal_2
            lambda_idler_1 = self.lambda_idler_1
            lambda_idler_2 = self.lambda_idler_2
            lambda_pump = self.lambda_pump
            # WBG_period = self.WBG_period
            m = self.m
            gap_x = self.gap_x
            gap_y = self.gap_y
            # calculate grating period via lambda
            # factor = 1
            # period_signal = self.lambda_signal/factor
            # period_idler = self.lambda_idler/factor
            total_length = self.total_length
            EBL_scan_filed_length = self.EBL_scan_filed_length
            GAP_WBG_WG_Y = self.GAP_WBG_WG_Y
            GAP_GACDC_WBG_Y = self.GAP_GACDC_WBG_Y
            insts_insts = {
                'WaveguideSource': BPFDcWaveguide(
                    lambda_pump=lambda_pump,
                    total_length=total_length
                ),
                'Cascaded_WBG': CompactCascadedWBG_HV(period=self.WBG_period),
                'output': GACDCFourChannel(
                    lambda_signal_1=lambda_signal_1,
                    lambda_signal_2=lambda_signal_2,
                    lambda_idler_1=lambda_idler_1,
                    lambda_idler_2=lambda_idler_2
                ),
                'Ring': Ring_doubleBus_160(),
                # 'input_through': TempPort(),
                # 'input_add': TempPort(),
            }

            # if m == 1:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.15)
            # elif m == 2:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.2969)
            # elif m == 3:
            #     insts_insts['Cascaded_WBG'] = CompactCascadedWBG_1(period=0.2940)

            insts_specs = [
                i3.Place('WaveguideSource:in', (0, 0)),
                i3.FlipV('Cascaded_WBG'),
                i3.PlaceRelative('Cascaded_WBG:in', 'WaveguideSource:out',
                                 (EBL_scan_filed_length, 0)),
                i3.FlipV('output'),
                i3.PlaceRelative('output:in', 'Cascaded_WBG:out',
                                 (EBL_scan_filed_length-40 , GAP_GACDC_WBG_Y)),
                i3.PlaceRelative('Ring:in', 'output:in',
                                 (-400,-100)),
                # i3.ConnectManhattan([
                #     ('Cascaded_WBG:out', 'Ring:in'),
                #     ('output:in', 'Ring:drop'),
                #     # ('input_through:out', 'WaveguideSource:through'),
                #     # ('input_add:out', 'WaveguideSource:add'),
                # ],
                #     bend_radius=20
                # ),
                i3.ConnectManhattan([
                    ('Ring:in', 'Cascaded_WBG:out'),
                    ('output:in', 'Ring:drop'),
                ],
                    bend_radius=20
                ),
                i3.ConnectManhattan([
                    ('WaveguideSource:out', 'Cascaded_WBG:in')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (960, 0)]
                ),
            ]
            #     i3.ConnectManhattan([
            #         ('WaveguideSource:out', 'Ring:in')
            #     ],
            #         bend_radius=20,
            #         control_points=[i3.START + (50, 100)]
            #     ),
            # ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.expose_ports(self.instances,
                                     {
                                         'WaveguideSource:in': 'in',
                                         # 'WaveguideSource:DC_out10': 'DC_out10',
                                         'output:signal_1': 'signal_1',
                                         'output:signal_2': 'signal_2',
                                         'output:idler_1': 'idler_1',
                                         'output:idler_2': 'idler_2',
                                         'output:through': 'through',
                                         'WaveguideSource:through': 'input_through',
                                         'WaveguideSource:add': 'input_add',
                                         'Ring:through':'ringthrough'
                                         # 'heater:elec1': 'elec2',
                                         # 'heater:elec2': 'elec1',
                                     })
            if self.heater_open:
                ports += i3.expose_ports(self.instances,
                                         {
                                             'WaveguideSource:elec1': 'elec1',
                                             'WaveguideSource:elec2': 'elec2',
                                             'Ring:elec1': 'elec11',
                                             'Ring:elec2': 'elec12',
                                             'Cascaded_WBG:elec1': 'elec3',
                                             'Cascaded_WBG:elec2': 'elec4',
                                             'Cascaded_WBG:elec3': 'elec5',
                                             'Cascaded_WBG:elec4': 'elec6',
                                             'Cascaded_WBG:elec5': 'elec7',
                                             'Cascaded_WBG:elec6': 'elec8',
                                             'Cascaded_WBG:elec7': 'elec9',
                                             'Cascaded_WBG:elec8': 'elec10',
                                             'output:elec1': 'elec13',
                                             'output:elec3': 'elec16',
                                             'output:elec5': 'elec17',
                                             'output:elec7': 'elec20',
                                             'output:elec2': 'elec14',
                                             'output:elec4': 'elec15',
                                             'output:elec6': 'elec18',
                                             'output:elec8': 'elec19',
                                         })
            return ports
if __name__ == '__main__':
    # pass
    lo = CompactIntegratedSourceElectricFlip_HV()
    #lo = CompactIntegratedSource(GAP_WBG_WG_Y=-200,)
    #lo = CompactIntegratedSource()
    #lo = CompactIntegratedSource()
    # lo = CompactIntegratedSourceRing()
    # lo.Layout().visualize(annotate=True)
    lo.Layout().write_gdsii('CompactIntegratedSource_HV.gds')
