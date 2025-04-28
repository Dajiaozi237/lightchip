import numpy as np
from si_fab import all as pdk
from ipkiss3 import all as i3
from Integrated_Source_pcell import \
    CompactIntegratedSource, CompactIntegratedSourceElectricFlip,CompactIntegratedSourceElectricFlip_HV
from ECrow_Pcell import ECrow
from cell_DC9010 import Direction_coupler_90_10
from BondPad_Pcell import BondPad
from AMWBGwithArm_pcell import AMWBGwithArm, AMWBGwithArmScanField, AMWBGwithArm_sameside
from cell_ringDoubleBus import Ring_doubleBus,Ring_doubleBus_210,Ring_doubleBus_220,Ring_doubleBus_200,Ring_doubleBus_190,Ring_doubleBus_270,Ring_doubleBus_280
from GC import GC_A, GC_B, GC_C
from waveguide import customWavegudie
from rib_waveguide import customribWavegudie
from cell_tworing import twoRing_doubleBus
import math

TECH = pdk.TECH
tt = i3.ElectricalWireTemplate()
tt.Layout(width=10, layer=i3.TECH.PPLAYER.M1)
"""
set the desired lambda(in um)
"""

lambda_1_1 = [1.545, 1.521, 1.529, 1.551, 1.559]
lambda_1_2 = [1.545, 1.521, 1.529, 1.551, 1.559]
lambda_2_1 = [1.540, 1.514, 1.524, 1.546, 1.554]
lambda_2_2 = [1.540, 1.514, 1.524, 1.546, 1.554]
lambda_3_1 = [1.550, 1.526, 1.536, 1.556, 1.566]
lambda_3_2 = [1.550, 1.526, 1.536, 1.556, 1.566]

WBG_period_1 = [0.2965, 0.2965, 0.2965, 0.2965, 0.2965, 0.2965]

class TextPCell(i3.PCell):
    # _name_prefix = "TextGC"
    text = i3.StringProperty(doc='display', default=' ')

    class Layout(i3.LayoutView):
        # n_rows = i3.IntProperty(doc="Number of GC rows", default=0)
        def _generate_elements(self, elems):
            labelText = self.text
            elems = i3.PolygonText(
                layer=TECH.PPLAYER.DOC,
                # layer=TECH.PPLAYER.NONE,
                text=labelText,
                alignment=(i3.TEXT.ALIGN.LEFT, i3.TEXT.ALIGN.TOP),
                coordinate=(0, 0.),
                font=0, height=600
            )
            return elems

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name='LOC', position=(0, 0.), angle=0)
            return ports
class ChipCell_1(i3.PCell):

    textMarker = i3.BoolProperty(default=False, doc=".")
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_pads = i3.PositiveNumberProperty(default=320, doc='lateral gap between bondpads')
    gap_wires = i3.PositiveNumberProperty(default=30, doc='lateral gap between bondpads')
    length_up = i3.PositiveNumberProperty(default=11000, doc='upper spiral total length')
    length_down = i3.PositiveNumberProperty(default=11000, doc='lower spiral total length')
    length_EC = i3.PositiveNumberProperty(default=12800, doc='length between ECrows')
    HEIGHT_S1 = i3.FloatProperty(default=310, doc='height of source1')
    HEIGHT_S2 = i3.FloatProperty(default=-150, doc='height of source2')

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            length_up = self.length_up
            length_down = self.length_down
            gap_pads = self.gap_pads
            gap_wires = self.gap_wires
            length_EC = self.length_EC
            HEIGHT_S1 = self.HEIGHT_S1
            HEIGHT_S2 = self.HEIGHT_S2
            gcc32 = pdk.GCrow(n_rows=12,
                              gc_sep_y=250,
                              FA_marker_sep=4000,
                              )
            instances  = {
                "FA": gcc32,
                'ECrow': ECrow(n_rows=20,
                               ec_sep_y=127,
                               ),
                'Source': CompactIntegratedSource(
                    lambda_pump=lambda_1_1[0],
                    total_length=length_down,
                    lambda_signal_1=lambda_1_1[2],
                    lambda_signal_2=lambda_1_1[1],
                    lambda_idler_1=lambda_1_1[3],
                    lambda_idler_2=lambda_1_1[4],
                    WBG_period=0.2965,
                ),
                'Source_2': CompactIntegratedSourceElectricFlip(
                    # m=1,
                    lambda_pump=lambda_1_2[0],
                    total_length=length_up,
                    lambda_signal_1=lambda_1_2[2],
                    lambda_signal_2=lambda_1_2[1],
                    lambda_idler_1=lambda_1_2[3],
                    lambda_idler_2=lambda_1_2[4],
                    WBG_period=0.2965,
                    GAP_GACDC_WBG_Y=100
                ),
                'FA1': GC_A(),
                'wave1': customWavegudie(
                n_o_waveguide=2,
                Width2=0.334,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127,
                # bendRadius=10,
                # rounding_algorithm=ra,
                ),
                'wave2': customWavegudie(
                n_o_waveguide=4,
                Width2=0.334,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127/3,
                # bendRadius=10,
                # rounding_algorithm=ra,
                ),
                'wave3': customWavegudie(
                n_o_waveguide=4,
                Width2=0.334,
                taperLength=200,
                Length=2500,
                gapBetweenWg=127/3,
                # bendRadius=10,
                # rounding_algorithm=ra,
                ),
                'text': TextPCell(text='1')
            }
            specs = [
                i3.Place("FA1:origin", (-3020, 430), angle=90),
                i3.Place('text:LOC', (1500, 300)),
                i3.Place("FA:wg_1", (-length_EC / 2, -1379)),
                i3.FlipH("ECrow"),
                i3.Place("ECrow:wg_1", (length_EC / 2, -1205)),
                i3.PlaceRelative('Source:in', 'FA:wg_2', (460, HEIGHT_S1)),
                i3.FlipV("Source_2"),
                i3.PlaceRelative('Source_2:in', 'FA:wg_11', (470, HEIGHT_S2)),
                i3.FlipH("wave1"),
                i3.PlaceRelative('wave1:in', 'ECrow:wg_8', (0, 0)),
                i3.FlipH("wave2"),
                i3.PlaceRelative('wave2:in', 'ECrow:wg_10', (-50, 0)),
                i3.FlipH("wave3"),
                i3.PlaceRelative('wave3:in', 'ECrow:wg_12', (-50, 0)),
                i3.ConnectManhattan([
                    ('FA:wg_7', 'FA:wg_6')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (100, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_9', 'wave1:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_11', 'wave2:out')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_13', 'wave3:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_8', 'wave1:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_10', 'wave2:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_12', 'wave3:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_3','Source:input_add')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -50)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_4','Source:input_through')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (200, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:in', 'FA:wg_5')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:ringthrough', 'FA:wg_2')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -500),
                                    i3.END + (50, -50)
                                    ]
                ),
                i3.ConnectManhattan([
                    ('Source_2:ringthrough', 'FA:wg_11')
                ],
                    bend_radius=20,
                    control_points=[
                        i3.START + (-150, 200),
                        i3.START + (-3000, 500),
                        i3.START + (-3500, 500),
                        # i3.START + (-3100, 700),
                        i3.END + (150, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_add', 'FA:wg_10')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_through', 'FA:wg_9')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (300, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:in', 'FA:wg_8')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (350, 50)]
                ),

                i3.ConnectManhattan([
                    ('ECrow:wg_1', 'ECrow:wg_2')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, -200), i3.END + (-100, -150)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_20', 'ECrow:wg_19')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-200, 0), i3.END + (-50, 50)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_1", 'ECrow:wg_7'),
                    ],
                    bend_radius=20,
                    control_points=[
                                    i3.END + (-900, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_2", 'ECrow:wg_6'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-800, -30)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:through", 'ECrow:wg_5'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-600, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_2", 'ECrow:wg_4'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-420, -340)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_1", 'ECrow:wg_3'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-200, -190)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_1', "ECrow:wg_14"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (600, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_2', "ECrow:wg_15"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (700, -200)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:through', "ECrow:wg_16"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (800, -200),]
                                    # i3.END + (400, 100)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_2', "ECrow:wg_17",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (900, -200),]
                                    # i3.END + (450, 150)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_1', "ECrow:wg_18",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (1000, -200),]
                                    # i3.END + (500, 100)]
                ),
            ]
            num_pads = 20  # the number of electric bondpads
            instances_electric = {}
            for i in range(num_pads):
                instances_electric["bp_s_{}".format(i + 1)] = BondPad()
                instances_electric["bp_n_{}".format(i + 1)] = BondPad()
            for i in range(4):
                instances_electric["bp{}".format(i + 1)] = BondPad()
            for i in range(4):
                instances_electric["bp{}".format(i + 5)] = BondPad()


            instances_electric['bp_1'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            instances_electric['bp_2'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            specs_electric = []
            for i in range(num_pads):
                specs_electric.append(i3.FlipV("bp_n_{}".format(i + 1)))

            for i in range(4):
                specs_electric.append(i3.FlipV("bp{}".format(i + 1)))

            pos_x = []  # lateral position of BondPad
            for i in range(num_pads):
                pos_x.append((i - int(num_pads / 2)) * gap_pads)
            for i in range(num_pads):
                specs_electric.append(
                    i3.Place("bp_s_{}".format(i + 1), (pos_x[i]-450, -1930))
                )
                specs_electric.append(
                    i3.Place("bp_n_{}".format(i + 1), (pos_x[19 - i] + gap_pads +0, 1930))
                )

            for i in range(4):
                specs_electric.append(
                    i3.Place("bp{}".format(i + 1), (gap_pads * (i + 11), 1930))
                )
            for i in range(4):
                specs_electric.append(
                    i3.Place("bp{}".format(i + 5), (gap_pads * (i + 9)-130, -1930))
                )

            specs_electric.append(i3.Place('bp_1', (-4200, -50))),
            specs_electric.append(i3.Place('bp_2', (2700, -50)))
            """
            routing electrical wires to the lower side Bondpad
            """

            control_points_s_y = [0, 0]
            control_points_s_y[0] = -1350
            control_points_s_y[1] = control_points_s_y[0] + gap_wires
            for i in range(7):
                control_points_s_y.append(-1380 + (i + 2) * gap_wires)
            for i in range(11):
                control_points_s_y.append(-1100 - i * gap_wires)

            control_points_s_x_2 = [0, 0]
            control_points_s_x_2[0] = -4500
            control_points_s_x_2[1] = control_points_s_x_2[0] + gap_wires
            for i in range(9):
                control_points_s_x_2.append((i - 10) * gap_wires)
            for i in range(9):
                control_points_s_x_2.append(i * gap_wires)
            control_points_s_y_2 = []
            for i in range(num_pads):
                if i != 0 and i != 1:
                    if control_points_s_x_2[i] <= pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1660 + (int(num_pads / 2) - i) * gap_wires
                        )
                    if control_points_s_x_2[i] > pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1700 + (i - int(num_pads / 2)) * gap_wires
                        )
                if i == 0:
                    control_points_s_y_2.append(
                        -1600
                    )
                if i == 1:
                    control_points_s_y_2.append(
                        -1570
                    )
            print(control_points_s_y),
            for i in range(num_pads):
                specs_electric.append(
                    i3.ConnectManhattan(
                        [
                            ('Source:elec{}'.format(i + 1), "bp_s_{}:port".format(i + 1))
                        ],
                        control_points=[
                            # i3.V(control_points_s_x[i]),
                            i3.H(control_points_s_y[i]),
                            i3.V(control_points_s_x_2[i]),
                            i3.H(control_points_s_y_2[i]),
                        ],
                    )
                )

            """
                routing electrical wires to the upper side Bondpad
            """


            control_points_n_y = [0, 0]
            control_points_n_y[0] = 1600
            control_points_n_y[1] = control_points_n_y[0] - gap_wires
            for i in range(7):
                control_points_n_y.append(1500 - gap_wires * 2 - i * gap_wires)
            for i in range(11):
                control_points_n_y.append(1100 + i * gap_wires)

            control_points_n_x_2 = [0,0]
            control_points_n_x_2[0]=-5000
            control_points_n_x_2[1] = -4030
            for i in range(7):
                control_points_n_x_2.append((i-10) * gap_wires)
            for i in range(11):
                control_points_n_x_2.append( (i+2) * gap_wires)

            control_points_n_y_2 = [0,0]
            control_points_n_y_2[0]=1600
            control_points_n_y_2[1] = 1570
            for i in range(num_pads-2):
                if control_points_n_x_2[i+2] < pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1800 + (i-int(num_pads / 2) ) * gap_wires
                    )
                if control_points_n_x_2[i+2] >= pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1670 + (int(num_pads / 2)-i-2) * gap_wires
                    )
            for i in range(num_pads):
                if i!=9:
                        specs_electric.append(
                            i3.ConnectManhattan(
                                [
                                    ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20-i))
                                ],
                                control_points=[
                                    # i3.V(control_points_n_x[i]),
                                    i3.H(control_points_n_y[i]),
                                    i3.V(control_points_n_x_2[i]),
                                    i3.H(control_points_n_y_2[i]),
                                ],
                            )
                        )
                if i==9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                # i3.V(control_points_n_x[i]),
                                i3.H(control_points_n_y[i]),
                                # i3.V(control_points_n_x_2[i]),
                                # i3.H(control_points_n_y_2[i]),
                            ],
                        )
                    )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec1', "bp1:port")
                    ],
                    control_points=[
                        i3.H(350),
                        i3.V(1220),
                        i3.H(650),
                        i3.V(5500),
                        i3.H(1430),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec2', "bp2:port")
                    ],
                    control_points=[
                        i3.V(1250),
                        i3.H(620),
                        i3.V(5530),
                        i3.H(1460),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec4', "bp3:port")
                    ],
                    control_points=[
                        i3.H(150),
                        i3.V(1280),
                        i3.H(590),
                        i3.V(5560),
                        i3.H(1490),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec3', "bp4:port")
                    ],
                    control_points=[
                        i3.V(100),
                        i3.H(100),
                        i3.V(1310),
                        i3.H(560),
                        i3.V(5590),
                        i3.H(1520),
                    ],
                )
            )
# down pad
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec5', "bp5:port")
                    ],
                    control_points=[
                        # i3.H(140),
                        i3.V(-920),
                        i3.H(-690),
                        i3.V(5300),
                        i3.H(-1510),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec6', "bp6:port")
                    ],
                    control_points=[
                        i3.V(-880),
                        i3.H(-660),
                        i3.V(5330),
                        i3.H(-1540),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec7', "bp7:port")
                    ],
                    control_points=[
                        # i3.H(140),
                        i3.V(-640),
                        i3.H(-630),
                        i3.V(5360),
                        i3.H(-1570),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA1:elec8', "bp8:port")
                    ],
                    control_points=[
                        i3.V(-610),
                        i3.H(-600),
                        i3.V(5390),
                        i3.H(-1600),
                    ],
                )
            )
            # put the dictionary instances and instances_electric together
            instances = {**instances, **instances_electric}
            # put the list specs and specs_electric together
            specs = specs + specs_electric
            insts = i3.place_and_route(insts=instances, specs=specs)
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            return ports
class ChipCell_2(i3.PCell):

    textMarker = i3.BoolProperty(default=False, doc=".")
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_pads = i3.PositiveNumberProperty(default=320, doc='lateral gap between bondpads')
    gap_wires = i3.PositiveNumberProperty(default=30, doc='lateral gap between bondpads')
    length_up = i3.PositiveNumberProperty(default=11000, doc='upper spiral total length')
    length_down = i3.PositiveNumberProperty(default=11000, doc='lower spiral total length')
    length_EC = i3.PositiveNumberProperty(default=12800, doc='length between ECrows')
    HEIGHT_S1 = i3.FloatProperty(default=250, doc='height of source1')
    HEIGHT_S2 = i3.FloatProperty(default=-80, doc='height of source2')

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            length_up = self.length_up
            length_down = self.length_down
            gap_pads = self.gap_pads
            gap_wires = self.gap_wires
            length_EC = self.length_EC
            HEIGHT_S1 = self.HEIGHT_S1
            HEIGHT_S2 = self.HEIGHT_S2
            WBG_1_1 = 0.22
            gcc32 = pdk.GCrow(n_rows=12,
                              gc_sep_y=250,
                              FA_marker_sep=4000,
                              )
            instances  = {
                "FA": gcc32,
                'ECrow': ECrow(n_rows=20,
                               ec_sep_y=127,
                               ),
                'Source': CompactIntegratedSource(
                    lambda_pump=lambda_2_1[0],
                    total_length=length_down,
                    lambda_signal_1=lambda_2_1[2],
                    lambda_signal_2=lambda_2_1[1],
                    lambda_idler_1=lambda_2_1[3],
                    lambda_idler_2=lambda_2_1[4],
                    WBG_period=0.2965,
                ),
                'Source_2': CompactIntegratedSourceElectricFlip_HV(
                    # m=1,
                    lambda_pump=lambda_2_2[0],
                    total_length=length_up,
                    lambda_signal_1=lambda_2_2[2],
                    lambda_signal_2=lambda_2_2[1],
                    lambda_idler_1=lambda_2_2[3],
                    lambda_idler_2=lambda_2_2[4],
                    WBG_period=0.2965,
                    GAP_GACDC_WBG_Y=100,
                ),
                'FA2': GC_B(),
                'wave1': customribWavegudie(
                n_o_waveguide=4,
                Width3=1,
                Width2=0.5,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127/3,
                ),
                'wave2': customribWavegudie(
                n_o_waveguide=4,
                Width2=0.55,
                Width3=1,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127/3,
                ),
                'wave3': customribWavegudie(
                n_o_waveguide=4,
                Width3=1,
                Width2=0.6,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127/3,
                ),
                'text': TextPCell(text='2')
            }
            specs = [
                i3.Place("FA2:origin", (-2500, 300), angle=90),
                i3.Place('text:LOC', (2200, 300)),
                i3.Place("FA:wg_1", (-length_EC / 2, -1379)),
                i3.FlipH("ECrow"),
                i3.Place("ECrow:wg_1", (length_EC / 2, -1205)),
                i3.PlaceRelative('Source:in', 'FA:wg_2', (460, HEIGHT_S1)),
                i3.FlipV("Source_2"),
                i3.PlaceRelative('Source_2:in', 'FA:wg_11', (470, HEIGHT_S2)),
                i3.FlipH("wave1"),
                i3.PlaceRelative('wave1:in', 'ECrow:wg_8', (-50, 0)),
                i3.FlipH("wave2"),
                i3.PlaceRelative('wave2:in', 'ECrow:wg_10', (-50, 0)),
                i3.FlipH("wave3"),
                i3.PlaceRelative('wave3:in', 'ECrow:wg_12', (-50, 0)),
                i3.ConnectManhattan([
                    ('ECrow:wg_9', 'wave1:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_11', 'wave2:out')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_13', 'wave3:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_8', 'wave1:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_10', 'wave2:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_12', 'wave3:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_7', 'FA:wg_6')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (100, 0)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_3','Source:input_add')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -50)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_4','Source:input_through')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (200, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:in', 'FA:wg_5')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:ringthrough', 'FA:wg_2')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -500),
                                    i3.END + (50, -50)
                                    ]
                ),
                i3.ConnectManhattan([
                    ('Source_2:ringthrough', 'FA:wg_11')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (-150, 200),
                                    i3.START + (-3000, 550),
                                    i3.START + (-3500, 550),
                                    # i3.START + (-3100, 700),
                                    i3.END + (150, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_add', 'FA:wg_10')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_through', 'FA:wg_9')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (300, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:in', 'FA:wg_8')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (350, 50)]
                ),

                i3.ConnectManhattan([
                    ('ECrow:wg_1', 'ECrow:wg_2')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, -200), i3.END + (-100, -150)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_20', 'ECrow:wg_19')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-200, 0), i3.END + (-50, 50)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_1", 'ECrow:wg_7'),
                    ],
                    bend_radius=20,
                    control_points=[
                        i3.END + (-900, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_2", 'ECrow:wg_6'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-800, -30)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:through", 'ECrow:wg_5'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-600, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_2", 'ECrow:wg_4'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-420, -340)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_1", 'ECrow:wg_3'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-200, -190)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_1', "ECrow:wg_14"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (600, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_2', "ECrow:wg_15"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (700, -200)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:through', "ECrow:wg_16"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (800, -200),]
                                    # i3.END + (400, 100)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_2', "ECrow:wg_17",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (900, -200),]
                                    # i3.END + (450, 150)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_1', "ECrow:wg_18",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (1000, -200),]
                                    # i3.END + (500, 100)]
                ),
            ]
            num_pads = 20  # the number of electric bondpads
            instances_electric = {}
            for i in range(num_pads):
                instances_electric["bp_s_{}".format(i + 1)] = BondPad()
                instances_electric["bp_n_{}".format(i + 1)] = BondPad()
            for i in range(4):
                instances_electric["bp{}".format(i + 1)] = BondPad()
            # for i in range(4):
            #     instances_electric["bp{}".format(i + 5)] = BondPad()

            instances_electric['bp_1'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            instances_electric['bp_2'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            specs_electric = []
            for i in range(num_pads):
                specs_electric.append(i3.FlipV("bp_n_{}".format(i + 1)))

            for i in range(4):
                specs_electric.append(i3.FlipV("bp{}".format(i + 1)))

            pos_x = []  # lateral position of BondPad
            for i in range(num_pads):
                pos_x.append((i - int(num_pads / 2)) * gap_pads)
            for i in range(num_pads):
                specs_electric.append(
                    i3.Place("bp_s_{}".format(i + 1), (pos_x[i] - 450, -1930))
                )
                specs_electric.append(
                    i3.Place("bp_n_{}".format(i + 1), (pos_x[19 - i] + gap_pads + 0, 1930))
                )

            for i in range(4):
                specs_electric.append(
                    i3.Place("bp{}".format(i + 1), (gap_pads * (i + 11), 1930))
                )
            # for i in range(4):
            #     specs_electric.append(
            #         i3.Place("bp{}".format(i + 5), (gap_pads * (i + 9) - 130, -1930))
            #     )

            specs_electric.append(i3.Place('bp_1', (-4600, 50))),
            specs_electric.append(i3.Place('bp_2', (3400, -50)))
            """
            routing electrical wires to the lower side Bondpad
            """

            control_points_s_y = [0, 0]
            control_points_s_y[0] = -1350
            control_points_s_y[1] = control_points_s_y[0] + gap_wires
            for i in range(7):
                control_points_s_y.append(-1380 + (i + 2) * gap_wires)
            for i in range(11):
                control_points_s_y.append(-1100 - i * gap_wires)

            control_points_s_x_2 = [0,0]
            control_points_s_x_2[0] = -4500
            control_points_s_x_2[1] = control_points_s_x_2[0] + gap_wires
            for i in range(9):
                control_points_s_x_2.append((i - 10) * gap_wires)
            for i in range(9):
                control_points_s_x_2.append(i * gap_wires)
            control_points_s_y_2 = []
            for i in range(num_pads):
                if i!=0 and i!=1:
                    if control_points_s_x_2[i] <= pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1660 + (int(num_pads / 2) - i) * gap_wires
                        )
                    if control_points_s_x_2[i] > pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1700 + (i - int(num_pads / 2)) * gap_wires
                        )
                if i==0:
                    control_points_s_y_2.append(
                        -1600
                    )
                if i==1:
                    control_points_s_y_2.append(
                        -1570
                    )
            print(control_points_s_y),
            for i in range(num_pads):
                specs_electric.append(
                    i3.ConnectManhattan(
                        [
                            ('Source:elec{}'.format(i + 1), "bp_s_{}:port".format(i + 1))
                        ],
                        control_points=[
                            # i3.V(control_points_s_x[i]),
                            i3.H(control_points_s_y[i]),
                            i3.V(control_points_s_x_2[i]),
                            i3.H(control_points_s_y_2[i]),
                        ],
                    )
                )

            """
                routing electrical wires to the upper side Bondpad
            """

            control_points_n_y = [0, 0]
            control_points_n_y[0] = 1600
            control_points_n_y[1] = control_points_n_y[0] - gap_wires
            for i in range(7):
                control_points_n_y.append(1500 - gap_wires * 2 - i * gap_wires)
            for i in range(11):
                control_points_n_y.append(1100 + i * gap_wires)

            control_points_n_x_2 = [0, 0]
            control_points_n_x_2[0] = -5000
            control_points_n_x_2[1] = -4030
            for i in range(7):
                control_points_n_x_2.append((i - 10) * gap_wires)
            for i in range(11):
                control_points_n_x_2.append((i + 2) * gap_wires)

            control_points_n_y_2 = [0, 0]
            control_points_n_y_2[0] = 1600
            control_points_n_y_2[1] = 1570
            for i in range(num_pads - 2):
                if control_points_n_x_2[i + 2] < pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1800 + (i  - int(num_pads / 2)) * gap_wires
                    )
                if control_points_n_x_2[i + 2] >= pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1670 + (int(num_pads / 2) - i - 2) * gap_wires
                    )
            for i in range(num_pads):
                if i!=6 and i!=7 and i!=5 and i!=9:
                        specs_electric.append(
                            i3.ConnectManhattan(
                                [
                                    ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                                ],
                                control_points=[
                                    # i3.V(control_points_n_x[i]),
                                    i3.H(control_points_n_y[i]),
                                    i3.V(control_points_n_x_2[i]),
                                    i3.H(control_points_n_y_2[i]),
                                ],
                            )
                        )
                if i==9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                i3.V(control_points_n_x_2[i]),
                                i3.H(control_points_n_y_2[i]-30),

                            ],
                        )
                    )
                if i==5:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                i3.V(-3200),
                                i3.H(control_points_n_y[i]),
                                i3.V(control_points_n_x_2[i]),
                                i3.H(control_points_n_y_2[i]),

                            ],
                        )
                    )
                if i==6:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                i3.V(-3150),
                                i3.H(control_points_n_y[i]),
                                i3.V(control_points_n_x_2[i]),
                                i3.H(control_points_n_y_2[i]),

                            ],
                        )
                    )
                if i==7:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                i3.V(-3100),
                                i3.H(control_points_n_y[i]),
                                i3.V(control_points_n_x_2[i]),
                                i3.H(control_points_n_y_2[i]),

                            ],
                        )
                    )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA2:elec1', "bp1:port")
                    ],
                    control_points=[
                        i3.H(300),
                        i3.V(1920),
                        i3.H(650),
                        i3.V(5500),
                        i3.H(1430),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA2:elec2', "bp2:port")
                    ],
                    control_points=[
                        i3.V(1950),
                        i3.H(620),
                        i3.V(5530),
                        i3.H(1460),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA2:elec4', "bp3:port")
                    ],
                    control_points=[
                        i3.H(50),
                        i3.V(1980),
                        i3.H(590),
                        i3.V(5560),
                        i3.H(1490),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA2:elec3', "bp4:port")
                    ],
                    control_points=[
                        i3.V(520),
                        i3.H(0),
                        i3.V(2010),
                        i3.H(560),
                        i3.V(5590),
                        i3.H(1520),
                    ],
                )
            )
            # # down pad
            # specs_electric.append(
            #     i3.ConnectManhattan(
            #         [
            #             ('Ring2:elec2', "bp5:port")
            #         ],
            #         control_points=[
            #             i3.H(250),
            #             i3.V(5700),
            #             i3.H(-300),
            #             i3.V(5300),
            #             i3.H(-1510),
            #         ],
            #     )
            # )
            # specs_electric.append(
            #     i3.ConnectManhattan(
            #         [
            #             ('Ring2:elec1', "bp6:port")
            #         ],
            #         control_points=[
            #             i3.V(5730),
            #             i3.H(-330),
            #             i3.V(5330),
            #             i3.H(-1540),
            #         ],
            #     )
            # )
            # specs_electric.append(
            #     i3.ConnectManhattan(
            #         [
            #             ('Ring1:elec2', "bp7:port")
            #         ],
            #         control_points=[
            #             i3.H(-100),
            #             i3.V(5760),
            #             i3.H(-360),
            #             i3.V(5360),
            #             i3.H(-1570),
            #         ],
            #     )
            # )
            # specs_electric.append(
            #     i3.ConnectManhattan(
            #         [
            #             ('Ring1:elec1', "bp8:port")
            #         ],
            #         control_points=[
            #             i3.V(5790),
            #             i3.H(-390),
            #             i3.V(5390),
            #             i3.H(-1600),
            #         ],
            #     )
            # )
            # put the dictionary instances and instances_electric together
            instances = {**instances, **instances_electric}
            # put the list specs and specs_electric together
            specs = specs + specs_electric
            insts = i3.place_and_route(insts=instances, specs=specs)
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            return ports
class ChipCell_3(i3.PCell):
    textMarker = i3.BoolProperty(default=False, doc=".")
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_pads = i3.PositiveNumberProperty(default=320, doc='lateral gap between bondpads')
    gap_wires = i3.PositiveNumberProperty(default=30, doc='lateral gap between bondpads')
    length_up = i3.PositiveNumberProperty(default=11000, doc='upper spiral total length')
    length_down = i3.PositiveNumberProperty(default=11000, doc='lower spiral total length')
    length_EC = i3.PositiveNumberProperty(default=12800, doc='length between ECrows')
    HEIGHT_S1 = i3.FloatProperty(default=200, doc='height of source1')
    HEIGHT_S2 = i3.FloatProperty(default=-360, doc='height of source2')

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            length_up = self.length_up
            length_down = self.length_down
            gap_pads = self.gap_pads
            gap_wires = self.gap_wires
            length_EC = self.length_EC
            HEIGHT_S1 = self.HEIGHT_S1
            HEIGHT_S2 = self.HEIGHT_S2
            WBG_1_1 = 0.22
            gcc32 = pdk.GCrow(n_rows=12,
                              gc_sep_y=250,
                              FA_marker_sep=4000,
                              )
            instances = {
                "FA": gcc32,
                'ECrow': ECrow(n_rows=20,
                               ec_sep_y=127,
                               ),
                'Source': CompactIntegratedSource(
                    lambda_pump=lambda_3_1[0],
                    total_length=length_down,
                    lambda_signal_1=lambda_3_1[2],
                    lambda_signal_2=lambda_3_1[1],
                    lambda_idler_1=lambda_3_1[3],
                    lambda_idler_2=lambda_3_1[4],
                    WBG_period=0.2965,
                ),
                'Source_2': CompactIntegratedSourceElectricFlip(
                    lambda_pump=lambda_3_2[0],
                    total_length=length_up,
                    lambda_signal_1=lambda_3_2[2],
                    lambda_signal_2=lambda_3_2[1],
                    lambda_idler_1=lambda_3_2[3],
                    lambda_idler_2=lambda_3_2[4],
                    WBG_period=0.2965,
                    GAP_GACDC_WBG_Y=100
                ),
                'wave1': customribWavegudie(
                n_o_waveguide=2,
                Width3=1,
                Width2=0.45,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127,
                ),
                'wave2': customribWavegudie(
                n_o_waveguide=4,
                Width2=0.45,
                Width3=1,
                taperLength=200,
                Length=2000,
                gapBetweenWg=127/3,
                # bendRadius=10,
                # rounding_algorithm=ra,
                ),
                'wave3': customribWavegudie(
                n_o_waveguide=4,
                Width3=1,
                Width2=0.45,
                taperLength=200,
                Length=2500,
                gapBetweenWg=127/3,
                # bendRadius=10,
                # rounding_algorithm=ra,
                ),
                'FA3': GC_C(),
                'text': TextPCell(text='3')
            }
            specs = [
                i3.Place("FA3:origin", (-3010, 290), angle=90),
                i3.Place('text:LOC', (1700, 300)),
                i3.Place("FA:wg_1", (-length_EC / 2, -1379)),
                i3.FlipH("ECrow"),
                i3.Place("ECrow:wg_1", (length_EC / 2, -1205)),
                i3.PlaceRelative('Source:in', 'FA:wg_2', (460, HEIGHT_S1)),
                i3.FlipV("Source_2"),
                i3.PlaceRelative('Source_2:in', 'FA:wg_11', (470, HEIGHT_S2)),
                i3.FlipH("wave1"),
                i3.PlaceRelative('wave1:in', 'ECrow:wg_8', (0, 0)),
                i3.FlipH("wave2"),
                i3.PlaceRelative('wave2:in', 'ECrow:wg_10', (-50, 0)),
                i3.FlipH("wave3"),
                i3.PlaceRelative('wave3:in', 'ECrow:wg_12', (-50, 0)),
                i3.ConnectManhattan([
                    ('ECrow:wg_9', 'wave1:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_11', 'wave2:out')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_13', 'wave3:out')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_8', 'wave1:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_10', 'wave2:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_12', 'wave3:in')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-500, 0),
                    #                 i3.END + (-5, -0),]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_7', 'FA:wg_6')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (100, 0)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_3', 'Source:input_add')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -50)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_4', 'Source:input_through')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (200, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:in', 'FA:wg_5')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, -50)]
                ),
                i3.ConnectManhattan([
                    ('Source:ringthrough', 'FA:wg_2')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (150, -500),
                                    i3.END + (50, -50)
                                    ]
                ),
                i3.ConnectManhattan([
                    ('Source_2:ringthrough', 'FA:wg_11')
                ],
                    bend_radius=20,
                    control_points=[i3.START + (-150, 200),
                                    i3.START + (-3000, 500),
                                    i3.START + (-3500, 500),
                                    # i3.START + (-3100, 700),
                                    i3.END + (150, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_add', 'FA:wg_10')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (250, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:input_through', 'FA:wg_9')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (300, 50)]
                ),
                i3.ConnectManhattan([
                    ('Source_2:in', 'FA:wg_8')
                ],
                    bend_radius=20,
                    control_points=[i3.END + (350, 50)]
                ),

                i3.ConnectManhattan([
                    ('ECrow:wg_1', 'ECrow:wg_2')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-50, -200), i3.END + (-100, -150)]
                ),
                i3.ConnectManhattan([
                    ('ECrow:wg_20', 'ECrow:wg_19')
                ],
                    bend_radius=20,
                    # control_points=[i3.START + (-200, 0), i3.END + (-50, 50)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_1", 'ECrow:wg_7'),
                    ],
                    bend_radius=20,
                    control_points=[
                        i3.END + (-900, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:signal_2", 'ECrow:wg_6'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-800, -30)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:through", 'ECrow:wg_5'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-600, -200)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_2", 'ECrow:wg_4'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-420, -340)]
                ),
                i3.ConnectManhattan(
                    [
                        ("Source:idler_1", 'ECrow:wg_3'),
                    ],
                    bend_radius=20,
                    control_points=[i3.END + (-200, -190)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_1', "ECrow:wg_14"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (600, -100)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:signal_2', "ECrow:wg_15"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (700, -50)]
                ),

                i3.ConnectManhattan(
                    [
                        ('Source_2:through', "ECrow:wg_16"),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (800, -200), ]
                    # i3.END + (400, 100)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_2', "ECrow:wg_17",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (900, -200), ]
                    # i3.END + (450, 150)]
                ),
                i3.ConnectManhattan(
                    [
                        ('Source_2:idler_1', "ECrow:wg_18",),
                    ],
                    bend_radius=20,
                    control_points=[i3.START + (1000, -200), ]
                    # i3.END + (500, 100)]
                ),
            ]
            num_pads = 20  # the number of electric bondpads
            instances_electric = {}
            for i in range(num_pads):
                instances_electric["bp_s_{}".format(i + 1)] = BondPad()
                instances_electric["bp_n_{}".format(i + 1)] = BondPad()
            for i in range(4):
                instances_electric["bp{}".format(i + 1)] = BondPad()
            for i in range(4):
                instances_electric["bp{}".format(i + 5)] = BondPad()

            instances_electric['bp_1'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            instances_electric['bp_2'] = BondPad(pad_width_x=850, pad_width_y=850, pad_open_width_x=840,
                                                 pad_open_width_y=840)
            specs_electric = []
            for i in range(num_pads):
                specs_electric.append(i3.FlipV("bp_n_{}".format(i + 1)))

            for i in range(4):
                specs_electric.append(i3.FlipV("bp{}".format(i + 1)))

            pos_x = []  # lateral position of BondPad
            for i in range(num_pads):
                pos_x.append((i - int(num_pads / 2)) * gap_pads)
            for i in range(num_pads):
                specs_electric.append(
                    i3.Place("bp_s_{}".format(i + 1), (pos_x[i] - 450, -1930))
                )
                specs_electric.append(
                    i3.Place("bp_n_{}".format(i + 1), (pos_x[19 - i] + gap_pads + 0, 1930))
                )

            for i in range(4):
                specs_electric.append(
                    i3.Place("bp{}".format(i + 1), (gap_pads * (i + 11), 1930))
                )
            for i in range(4):
                specs_electric.append(
                    i3.Place("bp{}".format(i + 5), (gap_pads * (i + 9) - 130, -1930))
                )

            specs_electric.append(i3.Place('bp_1', (-4000, -50))),
            specs_electric.append(i3.Place('bp_2', (2800, -50)))
            """
            routing electrical wires to the lower side Bondpad
            """

            control_points_s_y = [0, 0]
            control_points_s_y[0] = -1350
            control_points_s_y[1] = control_points_s_y[0] + gap_wires
            for i in range(8):
                control_points_s_y.append(-1380 + (i + 2) * gap_wires)
            for i in range(10):
                control_points_s_y.append(-1130 - i * gap_wires)

            control_points_s_x_2 = [0, 0]
            control_points_s_x_2[0] = -4500
            control_points_s_x_2[1] = control_points_s_x_2[0] + gap_wires
            for i in range(8):
                control_points_s_x_2.append((i - 10) * gap_wires)
            for i in range(10):
                control_points_s_x_2.append(i * gap_wires)
            #第一段y
            control_points_s_y_2 = []
            for i in range(num_pads):
                if i != 0 and i != 1:
                    if control_points_s_x_2[i] <= pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1630 + (int(num_pads / 2) - i) * gap_wires
                        )
                    if control_points_s_x_2[i] > pos_x[int(num_pads / 2)]:
                        control_points_s_y_2.append(
                            -1700 + (i - int(num_pads / 2)) * gap_wires
                        )
                if i == 0:
                    control_points_s_y_2.append(
                        -1600
                    )
                if i == 1:
                    control_points_s_y_2.append(
                        -1570
                    )
            print(control_points_s_y),
            for i in range(num_pads):
                if i !=9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source:elec{}'.format(i + 1), "bp_s_{}:port".format(i + 1))
                            ],
                            control_points=[
                                # i3.V(control_points_s_x[i]),
                                i3.H(control_points_s_y[i]),
                                i3.V(control_points_s_x_2[i]),
                                i3.H(control_points_s_y_2[i]),
                            ],
                        )
                    )
                if i ==9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source:elec{}'.format(i + 1), "bp_s_{}:port".format(i + 1))
                            ],
                            control_points=[
                                i3.H(control_points_s_y[i]),
                                i3.V(control_points_s_x_2[i]),
                                i3.H(control_points_s_y_2[i]),
                            ],
                        )
                    )

            """
                routing electrical wires to the upper side Bondpad
            """

            control_points_n_y = [0, 0]
            control_points_n_y[0] = 1600
            control_points_n_y[1] = control_points_n_y[0] - gap_wires
            for i in range(7):
                control_points_n_y.append(1500 - gap_wires * 2 - i * gap_wires)
            for i in range(11):
                control_points_n_y.append(1100 + i * gap_wires)

            control_points_n_x_2 = [0, 0]
            control_points_n_x_2[0] = -5000
            control_points_n_x_2[1] = -4030
            for i in range(7):
                control_points_n_x_2.append((i - 10) * gap_wires)
            for i in range(11):
                control_points_n_x_2.append((i + 2) * gap_wires)

            control_points_n_y_2 = [0, 0]
            control_points_n_y_2[0] = 1600
            control_points_n_y_2[1] = 1570
            for i in range(num_pads - 2):
                if control_points_n_x_2[i + 2] < pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1800 + (i  - int(num_pads / 2)) * gap_wires
                    )
                if control_points_n_x_2[i + 2] >= pos_x[int(num_pads / 2)]:
                    control_points_n_y_2.append(
                        1670 + (int(num_pads / 2) - i - 2) * gap_wires
                    )
            for i in range(num_pads):
                if i!=9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[
                                # i3.V(control_points_n_x[i]),
                                i3.H(control_points_n_y[i]),
                                i3.V(control_points_n_x_2[i]),
                                i3.H(control_points_n_y_2[i]),
                            ],
                        )
                    )
                if i==9:
                    specs_electric.append(
                        i3.ConnectManhattan(
                            [
                                ('Source_2:elec{}'.format(i + 1), "bp_n_{}:port".format(20 - i))
                            ],
                            control_points=[

                                # i3.H(control_points_n_y_2[i]),

                            ],
                        )
                    )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec1', "bp1:port")
                    ],
                    control_points=[
                        i3.H(300),
                        i3.V(1420),
                        i3.H(650),
                        i3.V(5500),
                        i3.H(1430),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec2', "bp2:port")
                    ],
                    control_points=[
                        i3.V(1450),
                        i3.H(620),
                        i3.V(5530),
                        i3.H(1460),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec4', "bp3:port")
                    ],
                    control_points=[
                        i3.H(0),
                        i3.V(1480),
                        i3.H(590),
                        i3.V(5560),
                        i3.H(1490),

                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec3', "bp4:port")
                    ],
                    control_points=[
                        i3.V(-100),
                        i3.H(-200),
                        i3.V(1510),
                        i3.H(560),
                        i3.V(5590),
                        i3.H(1520),

                    ],
                )
            )
            # down pad
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec5', "bp5:port")
                    ],
                    control_points=[
                        # i3.H(140),
                        i3.V(-1120),
                        i3.H(-690),
                        i3.V(5300),
                        i3.H(-1510),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec6', "bp6:port")
                    ],
                    control_points=[
                        i3.V(-1080),
                        i3.H(-660),
                        i3.V(5330),
                        i3.H(-1540),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec7', "bp7:port")
                    ],
                    control_points=[
                        # i3.H(140),
                        i3.V(-740),
                        i3.H(-630),
                        i3.V(5360),
                        i3.H(-1570),
                    ],
                )
            )
            specs_electric.append(
                i3.ConnectManhattan(
                    [
                        ('FA3:elec8', "bp8:port")
                    ],
                    control_points=[
                        i3.V(-710),
                        i3.H(-600),
                        i3.V(5390),
                        i3.H(-1600),
                    ],
                )
            )
            # put the dictionary instances and instances_electric together
            instances = {**instances, **instances_electric}
            # put the list specs and specs_electric together
            specs = specs + specs_electric
            insts = i3.place_and_route(insts=instances, specs=specs)
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            return ports
class IQLSChipLayout(i3.PCell):
    inner_square_length = i3.PositiveNumberProperty(default=14000, doc="the length of inner outline")
    outer_square_length = i3.PositiveNumberProperty(default=20000, doc="the length of outer outline")

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):

            x_spec = 1000
            y_spec = 1000
            # x_spec = 500
            # y_spec = 500
            i = 0
            chip_size = 14000
            frame_size = chip_size / 2
            # draw EBL scan field grids
            while (-frame_size + i * x_spec) <= frame_size:
                tempcoord = i3.Shape(i3.Coord2(-frame_size + i * x_spec, -frame_size)) \
                            + i3.Shape(i3.Coord2(-frame_size + i * x_spec, frame_size))

                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.FLOORPLAN,
                    # shape=tempcoord.modified_copy(closed=False),
                    shape=tempcoord,
                    line_width=0.
                )
                i = i + 1

            i = 0
            while (-frame_size + i * y_spec) <= frame_size:
                tempcoord = i3.Shape(i3.Coord2(-frame_size, -frame_size + i * y_spec)) \
                            + i3.Shape(i3.Coord2(frame_size, -frame_size + i * y_spec))

                elems += i3.Path(
                    layer=i3.TECH.PPLAYER.FLOORPLAN,
                    # shape=tempcoord.modified_copy(closed=False),
                    shape=tempcoord,
                    line_width=0.
                )
                i = i + 1

            inner_square_length = self.inner_square_length
            outer_square_length = self.outer_square_length
            elems += i3.RectanglePath(layer=i3.TECH.PPLAYER.FLOORPLAN,
                                      center=(0, 0),
                                      box_size=(outer_square_length, outer_square_length),
                                      line_width=2.0)
            elems += i3.RectanglePath(layer=i3.TECH.PPLAYER.FLOORPLAN,
                                      center=(0, 0),
                                      box_size=(inner_square_length, inner_square_length),
                                      line_width=2.0)
            elems += i3.Rectangle(layer=i3.TECH.PPLAYER.DOC,
                                      center=(0, 2400),
                                      box_size=(20000, 300),)
            elems += i3.Rectangle(layer=i3.TECH.PPLAYER.DOC,
                                      center=(0, -2400),
                                      box_size=(20000, 300),)
            elems += i3.Rectangle(layer=i3.TECH.PPLAYER.DOC,
                                  center=(0, 7200),
                                  box_size=(20000, 300), )
            elems += i3.Rectangle(layer=i3.TECH.PPLAYER.DOC,
                                  center=(0, -7200),
                                  box_size=(20000, 300), )
            return elems

        def _generate_instances(self, insts):

            instances = {
                'chip_1': ChipCell_1(
                    length_up=10000,
                    length_down=10000,
                    HEIGHT_S1=280,
                    HEIGHT_S2=-180
                ),
                'chip_2': ChipCell_2(
                    length_up=10000,
                    length_down=10000,
                    HEIGHT_S1=250,
                    HEIGHT_S2=-80,
                ),
                'chip_3': ChipCell_3(
                    length_up=10000,
                    length_down=10000,
                    HEIGHT_S1=200,
                    HEIGHT_S2=-360,
                ),
            }
            specs = [
                i3.Place("chip_1:origin", (0, 4800)),
                i3.Place("chip_2:origin", (0, 0)),
                i3.Place("chip_3:origin", (0, -4800)),
            ]
            insts = i3.place_and_route(insts=instances, specs=specs)
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            return ports

if __name__ == '__main__':
                # lo = ChipCell_2()
                # lo.Layout().write_gdsii('ChipCell_2.gds')
                lo=IQLSChipLayout()
                lo.Layout().write_gdsii('CHIP0113.gds')
