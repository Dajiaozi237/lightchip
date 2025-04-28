from si_fab import all as pdk
from ipkiss3 import all as i3
from GACDC_Pcell import GACDC_HT, GACDC_HT_ScanField, GACDCFourChannel
from GACDC_Pcell_Foundry import GACDC_HT_Foundry, GACDCFoundryArm
from CascadedWBG_Pcell import LongCascadedWBG, CompactCascadedWBG
from AMWBGwithArm_pcell import AMWBGwithArm, AMWBGwithArmScanField, AMWBGwithArm_sameside,AMWBGwithArm_sameside_reverse
from Ring import Ring_FSR200G_26, Ring_FSR200G_28, Ring_FSR200G_30, Ring_FSR200G_32, Ring_FSR200G_34, Ring_FSR200G_36, Ring_FSR200G_38, Ring_FSR200G_40, Ring_FSR200G_42, Ring_FSR200G_44, Ring_FSR200G_46
from cell_ringDoubleBus import Ring_doubleBus_230,Ring_doubleBus_210,Ring_doubleBus_240,Ring_doubleBus_200,Ring_doubleBus_220,Ring_doubleBus_190
from broadband_filters import Broad_WidthChirp_GuassApodized,Broad_WidthChirp_GuassApodized_HT
from cell_tworing import twoRing_doubleBus,twoRing_doubleBus_180,twoRing_doubleBus_12_6,twoRing_doubleBus_24_16,twoRing_doubleBus_160

import numpy as np
TECH = pdk.TECH


class custom_elec_single(i3.PCell):
    _name_prefix = "custom_elec"
    heater_width = i3.PositiveNumberProperty(default=3., doc="Width of the heater")
    heater_length = i3.PositiveNumberProperty(default=55., doc="heater_length")
    m1_taper_width = i3.PositiveNumberProperty(default=25., doc="Width of the M1 contact")
    m1_taper_length = i3.PositiveNumberProperty(default=25., doc="Length of the M1 contacst")
    m1_taper_wider = i3.PositiveNumberProperty(default=2., doc="M1 width of the end of M1 taper")
    overlap_heater_m1 = i3.PositiveNumberProperty(default=5., doc="overlap_heater_m1")

    class Layout(i3.LayoutView):
        def _generate_elements(self, elems):
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            m1_taper_wider = self.m1_taper_wider
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1

            elems += i3.Rectangle(layer=Lh,
                                  center=(0, 0),
                                  # box_size=(Width2, Length))
                                  box_size=(heater_length, heater_width))
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(-heater_length / 2 + overlap_heater_m1, 0),
                end_coord=(-heater_length / 2 - m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            elems += i3.Wedge(
                layer=Lm1,
                begin_coord=(heater_length / 2 - overlap_heater_m1, 0),
                end_coord=(heater_length / 2 + m1_taper_length, 0.),
                begin_width=heater_width + m1_taper_wider * 2,
                end_width=m1_taper_width,
            )
            return elems

        def _generate_ports(self, ports):
            wirewidth = 10
            heater_length = self.heater_length
            heater_width = self.heater_width
            m1_taper_width = self.m1_taper_width
            m1_taper_length = self.m1_taper_length
            overlap_heater_m1 = self.overlap_heater_m1
            tt = i3.ElectricalWireTemplate()
            tt.Layout(width=wirewidth, layer=i3.TECH.PPLAYER.M1)
            Lh = i3.TECH.PPLAYER.HT
            Lm1 = i3.TECH.PPLAYER.M1
            ports += i3.ElectricalPort(name='elec1',
                                       position=(heater_length / 2 + m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=0,
                                       trace_template=tt,
                                       )
            ports += i3.ElectricalPort(name='elec2',
                                       position=(-heater_length / 2 - m1_taper_length, 0),
                                       layer=i3.TECH.PPLAYER.M1,
                                       angle=180,
                                       trace_template=tt,
                                       )
            ports += i3.OpticalPort(name='left_loc_of_heater', position=(-heater_length / 2, 0), )
            return ports


class GC_A(i3.PCell):
    _name_prefix = "col_A"
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_y = i3.PositiveNumberProperty(default=150., doc="gap between grating coupler and device.")
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            gap_y = self.gap_y
            gcc32 = pdk.GCrow()
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            wbg_length = self.wbg_length
            num_GACDC=6
            insts_insts = {
                "FA": gcc32,

                'Ring1': Ring_doubleBus_190(heater_open=True),
                'Ring2': Ring_doubleBus_200(heater_open=True),
                'Ring3': Ring_doubleBus_210(heater_open=True),
                'Ring4': Ring_doubleBus_220(heater_open=True),
#宽度1μm
                'WBG1': AMWBGwithArm_sameside(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =0.295,
                                      apodization_type=apodization_type,
                                      heater_open=False,
                                      grating_width=0,
                                      ),
                'WBG2': AMWBGwithArm_sameside(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =0.298,
                                      apodization_type=apodization_type,
                                      heater_open=False,
                                      grating_width=0,
                                      ),
                'WBG3': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.295,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              wbg_waveguide_width=0.9
                                              ),
#四级级联WBG
                'WBG4': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2979,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG5': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2979,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG6': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2979,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG7': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2979,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
#回单级 改宽度0.9μm
                'WBG8': AMWBGwithArm_sameside(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.298,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              wbg_waveguide_width=0.9
                                              ),
                # 'GACDC7': GACDC_HT(lambda_resonance=1.54,
                #                    gap=0.38,
                #                    heater_open=False),
                'GACDC8': GACDC_HT(lambda_resonance=1.54,
                                   gap=0.38,
                                   heater_open=False),
                'GACDC9': GACDC_HT(lambda_resonance=1.56,
                                   gap=0.38,
                                   heater_open=False),
                # "BF7": Broad_WidthChirp_GuassApodized_HT(grating_period=0.34,
                #                                                       gap=0.08,
                #                                                       grating_width_drop_waveguide=0.14,
                #                                                       grating_width_bus_waveguide=0.1,
                #                                                       ),
            }
            insts_specs = [
                i3.Place("FA:wg_1", (0.0, 0.0)),
                i3.FlipH("WBG4"),
                i3.FlipV("WBG4"),
                i3.PlaceRelative('FA:wg_2', 'WBG4:out', (-50,0)),
                i3.PlaceRelative('WBG7:in', 'FA:wg_31', (300 , 0), angle=90),
                i3.FlipV("WBG5"),
                i3.PlaceRelative('WBG5:in', 'WBG7:out', (900, -400), angle=90),
                i3.FlipV("WBG6"),
                i3.PlaceRelative('WBG6:in', 'WBG5:out', (0, -300), angle=90),
                i3.ConnectManhattan([
                    ('WBG4:out', 'FA:wg_2'),
                ],
                    bend_radius=10,
                    control_points=[i3.END + (50,0)]
                ),
                i3.ConnectManhattan([
                    ('WBG7:out', 'WBG5:in'),
                ],
                    bend_radius=10,
                    control_points=[
                                   i3.START + (500, -50),
                                   ]
                ),
                i3.ConnectManhattan([
                    ('WBG5:out', 'WBG6:in'),
                ],
                    bend_radius=10,
                ),
                i3.ConnectManhattan([
                    ('WBG6:out', 'WBG4:in'),
                ],
                    bend_radius=10,
                ),
                i3.ConnectManhattan([
                    ('WBG7:in', 'FA:wg_31'),
                ],
                    bend_radius=10,
                ),

                i3.PlaceRelative('Ring1:in', 'FA:wg_29', (150, 0)),
                i3.PlaceRelative('Ring2:in', 'FA:wg_26', (150, 0)),
                i3.ConnectManhattan([
                    ('Ring1:in', 'FA:wg_29'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:through', 'FA:wg_28'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:drop', 'FA:wg_30'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (-20,0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:in', 'FA:wg_26'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:through', 'FA:wg_25'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:drop', 'FA:wg_27'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (-20,0)]
                ),

                i3.FlipH("GACDC8"),
                i3.PlaceRelative('GACDC8:through', 'FA:wg_4', (gap, 0)),
                i3.FlipH("GACDC9"),
                i3.PlaceRelative('GACDC9:through', 'FA:wg_7', (gap, 0)),
                # i3.FlipH("BF7"),
                # i3.PlaceRelative('BF7:through', 'FA:wg_10', (gap, 0)),
                # i3.FlipH("GACDC7"),
                # i3.PlaceRelative('GACDC7:through', 'FA:wg_13', (gap, 0)),

                i3.ConnectManhattan([
                    ('GACDC8:in', 'FA:wg_5'),
                    ('GACDC9:in', 'FA:wg_8'),
                    # ('BF7:in', 'FA:wg_9'),
                    # ('GACDC7:in', 'FA:wg_14'),
                ],
                ),
                i3.ConnectManhattan([
                    ('GACDC8:drop', 'FA:wg_3'),
                    ('GACDC9:drop', 'FA:wg_6'),
                    # ('BF7:drop', 'FA:wg_11'),
                    # ('GACDC7:drop', 'FA:wg_12'),
                ],
                ),
                i3.ConnectManhattan([
                    ('GACDC8:through', 'FA:wg_4'),
                    ('GACDC9:through', 'FA:wg_7'),
                    # ('BF7:through', 'FA:wg_10'),
                    # ('GACDC7:through', 'FA:wg_13'),
                ],
                ),

                i3.PlaceRelative('WBG1:in', 'FA:wg_9', (gap-50, 0)),
                i3.PlaceRelative('WBG2:in', 'FA:wg_11', (gap-50, 0)),
                i3.PlaceRelative('WBG3:in', 'FA:wg_13', (gap-50, 0)),
                i3.PlaceRelative('WBG8:in', 'FA:wg_15', (gap-50, 0)),
                i3.ConnectManhattan([
                    ('WBG1:in', 'FA:wg_9'),
                    ('WBG2:in', 'FA:wg_11'),
                    ('WBG3:in', 'FA:wg_13'),
                    ('WBG8:in', 'FA:wg_15'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('WBG1:out', 'FA:wg_10'),
                    ('WBG2:out', 'FA:wg_12'),
                    ('WBG3:out', 'FA:wg_14'),
                    ('WBG8:out', 'FA:wg_16'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (50, 20)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_23', 'FA:wg_24'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (100, 0)]
                ),
                i3.PlaceRelative('Ring3:in', 'FA:wg_18', (150, 0)),
                i3.PlaceRelative('Ring4:in', 'FA:wg_21', (150, 0)),
                i3.ConnectManhattan([
                    ('Ring3:in', 'FA:wg_18'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring3:through', 'FA:wg_17'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring3:add', 'FA:wg_19'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:in', 'FA:wg_21'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:through', 'FA:wg_20'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:add', 'FA:wg_22'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),

            ]

            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Ring1:elec1': 'elec1',
                                         'Ring1:elec2': 'elec2',
                                         'Ring2:elec1': 'elec3',
                                         'Ring2:elec2': 'elec4',
                                         'Ring3:elec1': 'elec5',
                                         'Ring3:elec2': 'elec6',
                                         'Ring4:elec1': 'elec7',
                                         'Ring4:elec2': 'elec8',
                                     })
            return ports


class GC_B(i3.PCell):
    _name_prefix = "col_A"
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_y = i3.PositiveNumberProperty(default=150., doc="gap between grating coupler and device.")
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)

    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            gap_y = self.gap_y
            gcc32 = pdk.GCrow()
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            wbg_length = self.wbg_length
            insts_insts = {
                "FA": gcc32,
                "BF1":Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                     gap=0.1,
                                                                     grating_width_drop_waveguide=0.16,
                                                                     grating_width_bus_waveguide=0.14,
                                                                     ),
                "BF2": Broad_WidthChirp_GuassApodized_HT(grating_period=0.33,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF3": Broad_WidthChirp_GuassApodized_HT(grating_period=0.34,
                                                                      gap=0.1,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF4": Broad_WidthChirp_GuassApodized_HT(grating_period=0.33,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
                "BF5": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.16,
                                                                      grating_width_bus_waveguide=0.14,
                                                                      ),
                "BF6": Broad_WidthChirp_GuassApodized_HT(grating_period=0.32,
                                                                      gap=0.08,
                                                                      grating_width_drop_waveguide=0.14,
                                                                      grating_width_bus_waveguide=0.1,
                                                                      ),
#宽度0.8μm
                'WBG1': AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.295,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              wbg_waveguide_width=0.8
                                              ),
#四级级联
                'WBG4': AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2988,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG5': AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2988,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG6': AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2988,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
                'WBG7': AMWBGwithArm_sameside_reverse(apFunction=apFunction,
                                              apodization=wbg_length / 2,
                                              wbg_length=wbg_length,
                                              period=0.2988,
                                              apodization_type=apodization_type,
                                              heater_open=False,
                                              grating_width=0,
                                              ),
#
                'Ring1': twoRing_doubleBus_160(heater_open=True),
                'Ring2': twoRing_doubleBus_12_6(heater_open=True),
            }

            insts_specs = [
                i3.Place("FA:wg_1", (0.0, 0.0)),

                i3.PlaceRelative('Ring1:in', 'FA:wg_29', (150, 0)),
                i3.PlaceRelative('Ring2:in', 'FA:wg_26', (150, 0)),
                i3.ConnectManhattan([
                    ('Ring1:in', 'FA:wg_29'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:through', 'FA:wg_28'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:add', 'FA:wg_30'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:in', 'FA:wg_26'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:through', 'FA:wg_25'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:add', 'FA:wg_27'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),

                i3.FlipH("WBG4"),
                i3.PlaceRelative('FA:wg_4', 'WBG4:out', (-50, 0)),
                i3.FlipV("WBG7"),
                i3.PlaceRelative('WBG7:in', 'FA:wg_31', (300, 0), angle=90),
                i3.FlipV("WBG5"),
                i3.PlaceRelative('WBG5:in', 'WBG7:out', (550, -200), angle=90),
                i3.FlipV("WBG6"),
                i3.PlaceRelative('WBG6:in', 'WBG5:out', (0, -200), angle=90),
                i3.ConnectManhattan([
                    ('WBG4:out', 'FA:wg_4'),
                ],
                    bend_radius=10,
                    control_points=[i3.END + (50, 0)]
                ),
                i3.ConnectManhattan([
                    ('WBG7:out', 'WBG5:in'),
                ],
                    bend_radius=10,
                    control_points=[
                        i3.START + (500, -50),
                    ]
                ),
                i3.ConnectManhattan([
                    ('WBG5:out', 'WBG6:in'),
                ],
                    bend_radius=10,
                ),
                i3.ConnectManhattan([
                    ('WBG6:out', 'WBG4:in'),
                ],
                    bend_radius=10,
                ),
                i3.ConnectManhattan([
                    ('WBG7:in', 'FA:wg_31'),
                ],
                    bend_radius=10,
                ),

                i3.FlipH("BF1"),
                i3.PlaceRelative('BF1:through', 'FA:wg_6', (gap, 0)),
                i3.FlipH("BF2"),
                i3.PlaceRelative('BF2:through', 'FA:wg_9', (gap, 0)),
                i3.FlipH("BF3"),
                i3.PlaceRelative('BF3:through', 'FA:wg_12', (gap, 0)),
                i3.FlipH("BF4"),
                i3.PlaceRelative('BF4:through', 'FA:wg_15', (gap, 0)),
                i3.FlipH("BF5"),
                i3.PlaceRelative('BF5:through', 'FA:wg_18', (gap, 0)),
                i3.FlipH("BF6"),
                i3.PlaceRelative('BF6:through', 'FA:wg_21', (gap, 0)),

                i3.ConnectManhattan([
                    ('BF1:in', 'FA:wg_5'),
                    ('BF2:in', 'FA:wg_8'),
                    ('BF3:in', 'FA:wg_11'),
                    ('BF4:in', 'FA:wg_14'),
                    ('BF5:in', 'FA:wg_17'),
                    ('BF6:in', 'FA:wg_20'),
                ],
                ),
                i3.ConnectManhattan([
                    ('BF1:through', 'FA:wg_6'),
                    ('BF2:through', 'FA:wg_9'),
                    ('BF3:through', 'FA:wg_12'),
                    ('BF4:through', 'FA:wg_15'),
                    ('BF5:through', 'FA:wg_18'),
                    ('BF6:through', 'FA:wg_21'),
                ],
                ),
                i3.ConnectManhattan([
                    ('BF1:drop', 'FA:wg_7'),
                    ('BF2:drop', 'FA:wg_10'),
                    ('BF3:drop', 'FA:wg_13'),
                    ('BF4:drop', 'FA:wg_16'),
                    ('BF5:drop', 'FA:wg_19'),
                    ('BF6:drop', 'FA:wg_22'),
                ],
                ),
                i3.PlaceRelative('WBG1:in', 'FA:wg_2', (gap, -50)),
                i3.ConnectManhattan([
                    ('WBG1:in', 'FA:wg_2'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (0, -20)]
                ),
                i3.ConnectManhattan([
                    ('WBG1:out', 'FA:wg_3'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (50, 20),
                    #                i3.END + (10, -50)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_23', 'FA:wg_24'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (100, 0)]
                ),
            ]


            insts += i3.place_and_route(
                insts=insts_insts,
                specs=insts_specs
            )
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Ring1:elec1': 'elec1',
                                         'Ring1:elec2': 'elec2',
                                         'Ring2:elec1': 'elec3',
                                         'Ring2:elec2': 'elec4',
                                     })

            return ports


class GC_C(i3.PCell):
    _name_prefix = "col_A"
    gap = i3.PositiveNumberProperty(default=110., doc="gap between grating coupler and device.")
    gap_y = i3.PositiveNumberProperty(default=150., doc="gap between grating coupler and device.")
    apodization = i3.NonNegativeNumberProperty(doc="", default=300.0)
    apFunction = i3.StringProperty(default="Blackman", doc="type of waveguide: wide or narrow")
    apodization_type = i3.StringProperty(default='DoubleSide', doc="type of waveguide: wide or narrow")
    wbg_length = i3.PositiveNumberProperty(doc=" ", default=850.0)
    class Layout(i3.LayoutView):
        def _generate_instances(self, insts):
            gap = self.gap
            gap_y = self.gap_y
            gcc32 = pdk.GCrow()
            apodization = self.apodization
            apFunction = self.apFunction
            apodization_type = self.apodization_type
            wbg_length = self.wbg_length
            num_GACDC=6
            insts_insts = {
                "FA": gcc32,

                'Ring1': twoRing_doubleBus_24_16(heater_open=True),
                'Ring2': twoRing_doubleBus_180(heater_open=True),
                'Ring3': Ring_doubleBus_230(heater_open=True),
                'Ring4': Ring_doubleBus_240(heater_open=True),
#宽度0.8μm
                'WBG1': AMWBGwithArm_sameside(apFunction=apFunction,
                                      apodization=wbg_length / 2,
                                      wbg_length=wbg_length,
                                      period =0.298,
                                      apodization_type=apodization_type,
                                      heater_open=False,
                                      grating_width=0,
                                      wbg_waveguide_width=0.8
                                      ),
                'GACDC7': GACDC_HT(lambda_resonance=1.54,
                                   gap=0.36,
                                   heater_open=False),
                'GACDC8': GACDC_HT(lambda_resonance=1.54,
                                   gap=0.37,
                                   heater_open=False),
                'GACDC9': GACDC_HT(lambda_resonance=1.54,
                                   gap=0.39,
                                   heater_open=False),
                'GACDC10': GACDC_HT(lambda_resonance=1.54,
                                    gap=0.4,
                                   heater_open=False),
            }
            insts_specs = [
                i3.Place("FA:wg_1", (0.0, 0.0)),

                i3.PlaceRelative('Ring1:in', 'FA:wg_29', (150, 0)),
                i3.PlaceRelative('Ring2:in', 'FA:wg_25', (150, 0)),
                i3.ConnectManhattan([
                    ('Ring1:in', 'FA:wg_29'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:through', 'FA:wg_28'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:add', 'FA:wg_31'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5,0)]
                ),
                i3.ConnectManhattan([
                    ('Ring1:drop', 'FA:wg_30'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (-5, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:in', 'FA:wg_25'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:through', 'FA:wg_24'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:add', 'FA:wg_27'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5,0)]
                ),
                i3.ConnectManhattan([
                    ('Ring2:drop', 'FA:wg_26'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (-5, 0)]
                ),

                i3.FlipH("GACDC8"),
                i3.PlaceRelative('GACDC8:through', 'FA:wg_3', (gap, 0)),
                i3.FlipH("GACDC9"),
                i3.PlaceRelative('GACDC9:through', 'FA:wg_6', (gap, 0)),
                i3.FlipH("GACDC10"),
                i3.PlaceRelative('GACDC10:through', 'FA:wg_9', (gap, 0)),
                i3.FlipH("GACDC7"),
                i3.PlaceRelative('GACDC7:through', 'FA:wg_12', (gap, 0)),

                i3.ConnectManhattan([
                    ('GACDC8:in', 'FA:wg_4'),
                    ('GACDC9:in', 'FA:wg_7'),
                    ('GACDC10:in', 'FA:wg_10'),
                    ('GACDC7:in', 'FA:wg_13'),
                ],
                ),
                i3.ConnectManhattan([
                    ('GACDC8:drop', 'FA:wg_2'),
                    ('GACDC9:drop', 'FA:wg_5'),
                    ('GACDC10:drop', 'FA:wg_8'),
                    ('GACDC7:drop', 'FA:wg_11'),
                ],
                ),
                i3.ConnectManhattan([
                    ('GACDC8:through', 'FA:wg_3'),
                    ('GACDC9:through', 'FA:wg_6'),
                    ('GACDC10:through', 'FA:wg_9'),
                    ('GACDC7:through', 'FA:wg_12'),
                ],
                ),

                i3.PlaceRelative('WBG1:in', 'FA:wg_14', (gap-50, 0)),
                # i3.PlaceRelative('WBG2:in', 'FA:wg_17', (gap-50, 0)),
                # i3.PlaceRelative('WBG3:in', 'FA:wg_19', (gap-50, 0)),
                # i3.PlaceRelative('WBG8:in', 'FA:wg_21', (gap-50, 0)),
                i3.ConnectManhattan([
                    ('WBG1:in', 'FA:wg_14'),
                    # ('WBG2:in', 'FA:wg_17'),
                    # ('WBG3:in', 'FA:wg_19'),
                    # ('WBG8:in', 'FA:wg_21'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('WBG1:out', 'FA:wg_15'),
                    # ('WBG2:out', 'FA:wg_18'),
                    # ('WBG3:out', 'FA:wg_20'),
                    # ('WBG8:out', 'FA:wg_22'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (50, 20)]
                ),
                i3.ConnectManhattan([
                    ('FA:wg_22', 'FA:wg_23'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (100, 0)]
                ),
                i3.PlaceRelative('Ring3:in', 'FA:wg_17', (150, 0)),
                i3.PlaceRelative('Ring4:in', 'FA:wg_20', (150, 0)),
                i3.ConnectManhattan([
                    ('Ring3:in', 'FA:wg_17'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring3:through', 'FA:wg_16'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring3:add', 'FA:wg_18'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:in', 'FA:wg_20'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (0, 0)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:through', 'FA:wg_19'),
                ],
                    bend_radius=10,
                    # control_points=[i3.START + (30, -30)]
                ),
                i3.ConnectManhattan([
                    ('Ring4:add', 'FA:wg_21'),
                ],
                    bend_radius=10,
                    control_points=[i3.START + (5, 0)]
                ),
            ]

            insts += i3.place_and_route(
                    insts=insts_insts,
                    specs=insts_specs
                )
            return insts

        def _generate_ports(self, ports):
            ports += i3.OpticalPort(name="origin", position=(0.0, 0.0), angle=180.0)
            ports += i3.expose_ports(self.instances,
                                     {
                                         'Ring1:elec1': 'elec1',
                                         'Ring1:elec2': 'elec2',
                                         'Ring2:elec1': 'elec3',
                                         'Ring2:elec2': 'elec4',
                                         'Ring3:elec1': 'elec5',
                                         'Ring3:elec2': 'elec6',
                                         'Ring4:elec1': 'elec7',
                                         'Ring4:elec2': 'elec8',
                                     })
            return ports

if __name__ == '__main__':
    lo = GC_B()
    lo.Layout().write_gdsii('GC_B.gds')
    # lo1 = GC_B()
    # lo1.Layout().write_gdsii('GC_B.gds')
    # lo2 = GC_C()
    # lo2.Layout().write_gdsii('GC_C.gds')
    # lo3 = Ring_MZI()
    # lo3.Layout().write_gdsii('Ring_MZI.gds')